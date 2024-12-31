import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.db import connections, connection
from time import sleep
from django.core.management import CommandError
# from property.models import RatingAndReview

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for generating hypothetical ratings and reviews'
    
    API_KEY = "AIzaSyBsiGjUOf5qbyylbqiYDokWhrGAlqpz7cw"
    
    def setup_model(self, api_key):
        """Configure and return the Gemini model"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            return model
        except Exception as e:
            raise CommandError(f"Error setting up model: {str(e)}")
    
    def generate_text(self, model, prompt, max_tokens, temperature):
        """Generate text using the Gemini model"""
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
            raise CommandError(f"Error generating text: {str(e)}")

    def handle(self, *args, **kwargs):
        try:
            # Truncate the RatingAndReview table to remove old data
            # with connection.cursor() as cursor:
            #     cursor.execute("TRUNCATE TABLE property_ratingandreview RESTART IDENTITY CASCADE;")
            
            # self.stdout.write(self.style.SUCCESS("RatingAndReview table truncated and ID sequence reset."))

            # Connect to the trip_db and fetch the hotel data
            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            # Hardcoded prompt for generating hypothetical rating and review
            prompt_template = (
                "Generate a hypothetical rating and review for a hotel named '{property_title}' "
                "located in {location}. The hotel has the following details: \n"
                "- Hotel ID: {hotel_id}\n"
                "- Price: {price}\n"
                "- Rating: {rating}\n"
                "- Address: {address}\n"
                "- Coordinates: Latitude: {latitude}, Longitude: {longitude}\n"
                "- Room Type: {room_type}\n"
                "Please generate a realistic rating (from 1 to 5) and a review for this hotel. "
                "The review should be engaging and helpful for future guests, based on the attributes above."
                "Please make sure the review is realistic and not too lengthy. The review should feel natural."
            )

            # Initialize the model
            model = self.setup_model(self.API_KEY)

            # Iterate through each row and send the property_title to API
            for row in rows:
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

                # Prepare the prompt using the hardcoded template with the new data
                prompt = prompt_template.format(
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

                # Generate text using the model
                rating_and_review = self.generate_text(
                    model,
                    prompt,
                    max_tokens=256,
                    temperature=0.7
                )
                
                # Add a small delay between requests to avoid rate limiting
                sleep(1)

                # Save the generated rating and review data to the database
                # rating_instance, created = RatingAndReview.objects.update_or_create(
                #     hotel_id=hotel_id,
                #     defaults={
                #         "rating": rating,
                #         "review": rating_and_review
                #     }
                # )

                # Output the hotel info with generated rating and review
                # action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(
                    f" Rating and Review for Hotel ID: {hotel_id}, Rating: {rating}, Review: {rating_and_review}"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
