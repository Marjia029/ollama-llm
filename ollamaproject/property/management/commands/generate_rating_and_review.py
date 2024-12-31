import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.db import connections, connection
from time import sleep
import time
from django.core.management import CommandError
from typing import Optional, Tuple, Any
from property.models import RatingAndReview

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for generating hypothetical ratings and reviews'
    
    API_KEY = "AIzaSyBsiGjUOf5qbyylbqiYDokWhrGAlqpz7cw"
    MAX_RETRIES = 3
    RETRY_DELAY = 60
    BATCH_SIZE = 5
    BATCH_DELAY = 10

    # Prompt templates
    RATING_PROMPT_TEMPLATE = (
        "Generate a hypothetical rating for a hotel named '{property_title}' "
        "located in {location}. The hotel has the following details: \n"
        "- Hotel ID: {hotel_id}\n"
        "- Price: {price}\n"
        "- Rating: {rating}\n"
        "- Address: {address}\n"
        "- Coordinates: Latitude: {latitude}, Longitude: {longitude}\n"
        "- Room Type: {room_type}\n"
        "Please generate a realistic rating (from 1 to 5) for this hotel based on the details provided."
        "Only give the rating in floating point. No other text."
    )

    REVIEW_PROMPT_TEMPLATE = (
        "Generate a hypothetical review for a hotel named '{property_title}' "
        "located in {location}. The hotel has the following details: \n"
        "- Hotel ID: {hotel_id}\n"
        "- Price: {price}\n"
        "- Your Generated Rating: {generated_rating} out of 5\n"
        "- Address: {address}\n"
        "- Room Type: {room_type}\n"
        "Please write a {sentiment} review that justifies the {generated_rating}/5 rating you gave. "
        "The review should be realistic and engaging, matching the rating level. "
        "Keep it concise, within 20 words. Only give the review text, no rating numbers."
    )

    def setup_model(self, api_key: str) -> Any:
        """Configure and return the Gemini model"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            return model
        except Exception as e:
            raise CommandError(f"Error setting up model: {str(e)}")

    def generate_text_with_retry(self, model: Any, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using the Gemini model with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': temperature,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': max_tokens,
                    }
                )
                return response.text
            except Exception as e:
                if "429" in str(e) and attempt < self.MAX_RETRIES - 1:
                    self.stdout.write(self.style.WARNING(
                        f"Rate limit hit, waiting {self.RETRY_DELAY} seconds before retry {attempt + 1}/{self.MAX_RETRIES}"
                    ))
                    time.sleep(self.RETRY_DELAY)
                    continue
                raise CommandError(f"Error generating text: {str(e)}")

    def get_review_sentiment(self, rating: float) -> str:
        """Determine review sentiment based on rating"""
        if rating >= 4.5:
            return "very positive"
        elif rating >= 4.0:
            return "positive"
        elif rating >= 3.0:
            return "neutral to positive"
        elif rating >= 2.0:
            return "somewhat negative"
        else:
            return "negative"

    def prepare_hotel_data(self, row: Tuple) -> dict:
        """Extract and prepare hotel data from database row"""
        return {
            'id': row[0],
            'location': row[1] if row[1] else None,
            'property_title': row[2] if row[2] else None,
            'hotel_id': row[3] if row[3] else None,
            'price': row[4] if row[4] else None,
            'rating': row[5] if row[5] else None,
            'address': row[6] if row[6] else None,
            'latitude': row[7] if row[7] else None,
            'longitude': row[8] if row[8] else None,
            'room_type': row[9] if row[9] else None,
        }

    def format_rating_prompt(self, hotel_data: dict) -> str:
        """Format rating prompt template with hotel data"""
        return self.RATING_PROMPT_TEMPLATE.format(
            property_title=hotel_data['property_title'] or "No Title",
            location=hotel_data['location'] or "Unknown Location",
            hotel_id=hotel_data['hotel_id'],
            price=hotel_data['price'] if hotel_data['price'] else "Not Available",
            rating=hotel_data['rating'] if hotel_data['rating'] else "Not Rated",
            address=hotel_data['address'] or "No Address Provided",
            latitude=hotel_data['latitude'] if hotel_data['latitude'] else "No Latitude Provided",
            longitude=hotel_data['longitude'] if hotel_data['longitude'] else "No Longitude Provided",
            room_type=hotel_data['room_type'] or "No Room Type Provided"
        )

    def format_review_prompt(self, hotel_data: dict, generated_rating: float) -> str:
        """Format review prompt template with hotel data and generated rating"""
        sentiment = self.get_review_sentiment(generated_rating)
        return self.REVIEW_PROMPT_TEMPLATE.format(
            property_title=hotel_data['property_title'] or "No Title",
            location=hotel_data['location'] or "Unknown Location",
            hotel_id=hotel_data['hotel_id'],
            price=hotel_data['price'] if hotel_data['price'] else "Not Available",
            generated_rating=generated_rating,
            address=hotel_data['address'] or "No Address Provided",
            room_type=hotel_data['room_type'] or "No Room Type Provided",
            sentiment=sentiment
        )

    def process_hotel(self, model: Any, hotel_data: dict) -> Optional[Tuple[str, str]]:
        """Process a single hotel and generate rating and review"""
        try:
            # Generate rating first
            rating_prompt = self.format_rating_prompt(hotel_data)
            generated_rating = float(self.generate_text_with_retry(
                model,
                rating_prompt,
                max_tokens=256,
                temperature=0.7
            ))

            # Use the generated rating to inform the review
            review_prompt = self.format_review_prompt(hotel_data, generated_rating)
            review = self.generate_text_with_retry(
                model,
                review_prompt,
                max_tokens=256,
                temperature=0.7
            )

            return str(generated_rating), review

        except CommandError as e:
            self.stdout.write(self.style.ERROR(
                f"Error processing hotel ID {hotel_data['hotel_id']}: {str(e)}"
            ))
            return None

    def truncate_ratings_table(self) -> None:
        """Truncate the ratings and reviews table and reset the ID sequence"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    TRUNCATE TABLE property_ratingandreview RESTART IDENTITY CASCADE;
                """)
            self.stdout.write(self.style.SUCCESS(
                "Successfully truncated property_ratingandreview table and reset ID sequence."
            ))
        except Exception as e:
            raise CommandError(f"Error truncating table: {str(e)}")

    def save_to_database(self, hotel_id: str, rating: float, review: str) -> None:
        """Save the generated rating and review to the database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO property_ratingandreview (hotel_id, rating, review)
                    VALUES (%s, %s, %s);
                    """,
                    [hotel_id, rating, review]
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving to database: {str(e)}"))

    def handle(self, *args, **kwargs):
        try:
            # First, truncate the table and reset ID sequence
            self.truncate_ratings_table()

            # Initialize the model
            model = self.setup_model(self.API_KEY)

            # Fetch hotel data
            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            # Process hotels in batches
            for i in range(0, len(rows), self.BATCH_SIZE):
                batch = rows[i:i + self.BATCH_SIZE]
                
                for row in batch:
                    hotel_data = self.prepare_hotel_data(row)
                    
                    # Process hotel
                    result = self.process_hotel(model, hotel_data)
                    
                    if result:
                        generated_rating, review = result
                        
                        # Save to database
                        self.save_to_database(
                            hotel_data['hotel_id'], 
                            float(generated_rating), 
                            review
                        )
                        
                        # Output results
                        self.stdout.write(self.style.SUCCESS(
                            f"ID: {hotel_data['id']}, "
                            f"Hotel_ID: {hotel_data['hotel_id']}, "
                            f"Rating: {generated_rating}, "
                            f"Review: {review}"
                        ))
                        
                        sleep(2)
                
                if i + self.BATCH_SIZE < len(rows):
                    self.stdout.write(self.style.WARNING(
                        f"Processed batch of {self.BATCH_SIZE} hotels. "
                        f"Waiting {self.BATCH_DELAY} seconds before next batch..."
                    ))
                    time.sleep(self.BATCH_DELAY)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))