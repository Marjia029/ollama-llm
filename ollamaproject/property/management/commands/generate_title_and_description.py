import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.db import connections
from time import sleep
from django.core.management import CommandError
from property.models import TitleAndDescription
import random
import logging
from datetime import datetime, timedelta
from config import GEMINI_API_KEY

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for title and description regeneration'
    
    # API_KEY = "AIzaSyBsiGjUOf5qbyylbqiYDokWhrGAlqpz7cw"
    
    def __init__(self):
        super().__init__()
        self.request_count = 0
        self.last_request_time = datetime.now()
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='generation_log.txt'
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
    
    def generate_text_with_retry(self, model, prompt, max_tokens, temperature, max_retries=3):
        """Generate text using the Gemini model with retry logic"""
        for attempt in range(max_retries):
            try:
                # Implement rate limiting
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
                    sleep(random.uniform(1, 3))  # Random delay between retries
    
    def _handle_rate_limiting(self):
        """Implement rate limiting logic"""
        # Basic rate limiting: max 60 requests per minute
        if self.request_count >= 60:
            time_diff = datetime.now() - self.last_request_time
            if time_diff < timedelta(minutes=1):
                sleep_time = 60 - time_diff.total_seconds()
                if sleep_time > 0:
                    self.logger.info(f"Rate limit approaching. Sleeping for {sleep_time} seconds")
                    sleep(sleep_time)
            self.request_count = 0
            self.last_request_time = datetime.now()
        
        # Add small random delay between requests
        sleep(random.uniform(0.5, 1.5))

    def handle(self, *args, **kwargs):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute('TRUNCATE TABLE property_titleanddescription RESTART IDENTITY CASCADE;')
            
            self.stdout.write(self.style.SUCCESS('Successfully truncated the table and reset IDs.'))

            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            title_prompt_template = (
                "Generate a catchy and SEO-friendly title for a hotel named '{property_title}' "
                "located in {location}. The hotel has the following details: \n"
                "- Hotel ID: {hotel_id}\n"
                "- Price: {price}\n"
                "- Rating: {rating}\n"
                "- Address: {address}\n"
                "- Coordinates: Latitude: {latitude}, Longitude: {longitude}\n"
                "- Room Type: {room_type}\n"
                "Please make the title creative, engaging, and SEO-friendly, "
                "considering the amenities and features listed above. "
                "The title should be different from {property_title}. Only give me the new title. Don't give any options."
            )

            description_prompt_template = (
                "Write a compelling and detailed description for a hotel named '{property_title}' "
                "located in {location}. Include the following details in a natural, engaging way:\n"
                "- Hotel ID: {hotel_id}\n"
                "- Price: {price}\n"
                "- Rating: {rating}\n"
                "- Address: {address}\n"
                "- Room Type: {room_type}\n"
                "The description should be in 30 words, highlighting the hotel's location, "
                "amenities, and unique features. Make it engaging for potential guests while "
                "maintaining SEO-friendliness. Focus on the value proposition and what makes "
                "this hotel special. Don't mention the hotel ID in the description."
            )

            model = self.setup_model(GEMINI_API_KEY)
            
            total_rows = len(rows)
            for index, row in enumerate(rows, 1):
                try:
                    id = row[0]
                    location = row[1] if row[1] else None
                    property_title = row[2] if row[2] else None
                    hotel_id = row[3] if row[3] else None
                    price = row[4] if row[4] else None
                    rating = row[5] if row[5] else None
                    address = row[6] if row[6] else None
                    latitude = row[7] if row[7] else None
                    longitude = row[8] if row[8] else None
                    room_type = row[9] if row[9] else None

                    self.logger.info(f"Processing hotel {index} of {total_rows} (ID: {hotel_id})")

                    title_prompt = title_prompt_template.format(
                        property_title=property_title or "No Title",
                        location=location or "Unknown Location",
                        hotel_id=hotel_id,
                        price=price if price else "Not Available",
                        rating=rating if rating else "Not Rated",
                        address=address or "No Address Provided",
                        latitude=latitude if latitude else "No Latitude Provided",
                        longitude=longitude if longitude else "No Longitude Provided",
                        room_type=room_type or "No Room Type Provided"
                    )

                    description_prompt = description_prompt_template.format(
                        property_title=property_title or "No Title",
                        location=location or "Unknown Location",
                        hotel_id=hotel_id,
                        price=price if price else "Not Available",
                        rating=rating if rating else "Not Rated",
                        address=address or "No Address Provided",
                        room_type=room_type or "No Room Type Provided"
                    )

                    regenerated_title = self.generate_text_with_retry(
                        model,
                        title_prompt,
                        max_tokens=256,
                        temperature=0.7
                    )

                    regenerated_description = self.generate_text_with_retry(
                        model,
                        description_prompt,
                        max_tokens=512,
                        temperature=0.7
                    )

                    regenerated_title_instance = TitleAndDescription(
                        hotel_id=hotel_id,
                        original_title=property_title,
                        regenerated_title=regenerated_title,
                        description=regenerated_description 
                    )
                    regenerated_title_instance.save()

                    self.stdout.write(self.style.SUCCESS(
                        f"Progress: {index}/{total_rows} ({(index/total_rows)*100:.1f}%)\n"
                        f"ID: {id}\n"
                        f"Hotel ID: {hotel_id}\n"
                        f"Original Title: {property_title}\n"
                        f"Generated Title: {regenerated_title}\n"
                        f"Generated Description: {regenerated_description}\n"
                        f"Location: {location}\n"
                        f"Price: {price}\n"
                        f"Rating: {rating}\n"
                        f"Address: {address}\n"
                        f"Coordinates: {latitude}, {longitude}\n"
                        f"Room Type: {room_type}\n"
                        f"-------------------"
                    ))

                except Exception as e:
                    self.logger.error(f"Error processing hotel {hotel_id}: {str(e)}")
                    self.stdout.write(self.style.ERROR(f"Error processing hotel {hotel_id}: {str(e)}"))
                    continue  # Continue with next hotel even if one fails

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.logger.error(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))