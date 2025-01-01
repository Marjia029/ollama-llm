import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.db import connections
from django.db import connection
from time import sleep
from django.core.management import CommandError
from django.core.management.color import no_style
from property.models import Summary
from config import GEMINI_API_KEY
import random
import logging
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for summary generation'
    
    def __init__(self):
        super().__init__()
        self.request_count = 0
        self.last_request_time = datetime.now()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='summary_generation_log.txt'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_model(self, api_key):
        """Configure and return the Gemini model"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            return model
        except Exception as e:
            self.logger.error(f"Error setting up model: {str(e)}")
            raise CommandError(f"Error setting up model: {str(e)}")
    
    def _handle_rate_limiting(self):
        """Implement rate limiting logic"""
        if self.request_count >= 60:  # Max 60 requests per minute
            time_diff = datetime.now() - self.last_request_time
            if time_diff < timedelta(minutes=1):
                sleep_time = 60 - time_diff.total_seconds()
                if sleep_time > 0:
                    self.logger.info(f"Rate limit approaching. Sleeping for {sleep_time} seconds")
                    sleep(sleep_time)
            self.request_count = 0
            self.last_request_time = datetime.now()
        
        # Add random delay between requests
        sleep(random.uniform(0.5, 1.5))

    def generate_text_with_retry(self, model, prompt, max_tokens, temperature, max_retries=3):
        """Generate text using the Gemini model with retry logic"""
        for attempt in range(max_retries):
            try:
                self._handle_rate_limiting()
                
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': temperature,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': max_tokens,
                    }
                )
                self.request_count += 1
                return response.text
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if "429" in str(e):  # Rate limit error
                    wait_time = (2 ** attempt) * 5  # Exponential backoff
                    self.logger.info(f"Rate limit reached. Waiting {wait_time} seconds...")
                    sleep(wait_time)
                elif attempt == max_retries - 1:  # Last attempt
                    raise CommandError(f"Final attempt failed: {str(e)}")
                else:
                    sleep(random.uniform(1, 3))

    def handle(self, *args, **kwargs):
        try:
            # Clear existing summaries using ORM
            Summary.objects.all().delete()

            # Reset the primary key sequence for the Summary model
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Summary])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

            self.stdout.write(self.style.SUCCESS("Summary table cleared successfully."))

            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            # Improved prompt for better summaries
            prompt_template = (
                "Create a compelling, concise summary (maximum 50 words) for a {room_type} at {property_title} "
                "in {location}. This {price} per night accommodation is rated {rating}.\n\n"
                "Focus on:\n"
                "1. Prime location: {address}\n"
                "2. Unique selling points\n"
                "3. Value proposition\n\n"
                "Make it inviting and memorable while highlighting the key features that make this hotel special. "
                "Craft a single, coherent summary that flows naturally and engages potential guests. "
                "Avoid listing features and focus on creating a narrative that captures the essence of the stay experience."
            )

            model = self.setup_model(GEMINI_API_KEY)
            
            total_rows = len(rows)
            for index, row in enumerate(rows, 1):
                try:
                    id = row[0]
                    location = row[1] if row[1] else None
                    property_title = row[2] if row[2] else None
                    hotel_id = row[3] if row[3] else None
                    price = f"${row[4]}" if row[4] else "Price on request"
                    rating = f"{row[5]}/5" if row[5] else "Unrated"
                    address = row[6] if row[6] else None
                    latitude = row[7] if row[7] else None
                    longitude = row[8] if row[8] else None
                    room_type = row[9] if row[9] else "Room"

                    self.logger.info(f"Processing hotel {index} of {total_rows} (ID: {hotel_id})")

                    prompt = prompt_template.format(
                        property_title=property_title or "No Title",
                        location=location or "Unknown Location",
                        hotel_id=hotel_id,
                        price=price,
                        rating=rating,
                        address=address or "Central Location",
                        latitude=latitude if latitude else "No Latitude Provided",
                        longitude=longitude if longitude else "No Longitude Provided",
                        room_type=room_type or "Room"
                    )

                    summary = self.generate_text_with_retry(
                        model,
                        prompt,
                        max_tokens=256,
                        temperature=0.7
                    )

                    summary_instance, created = Summary.objects.update_or_create(
                        hotel_id=hotel_id,
                        defaults={"summary": summary}
                    )

                    action = "Created" if created else "Updated"
                    self.stdout.write(self.style.SUCCESS(
                        f"Progress: {index}/{total_rows} ({(index/total_rows)*100:.1f}%)\n"
                        f"{action} Summary for Hotel ID: {hotel_id}\n"
                        f"Summary: {summary}\n"
                        f"-------------------"
                    ))

                except Exception as e:
                    error_msg = f"Error processing hotel {hotel_id}: {str(e)}"
                    self.logger.error(error_msg)
                    self.stdout.write(self.style.ERROR(error_msg))
                    continue  # Continue with next hotel even if one fails

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.logger.error(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))