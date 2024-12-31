import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.db import connections
from time import sleep
from django.core.management import CommandError

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for title regeneration'
    
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
            # Connect to the trip_db and fetch the hotel data
            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            # Hardcoded prompt for title regeneration with additional fields
            prompt_template = (
                "Generate a catchy and SEO-friendly title for a hotel named '{property_title}' "
                "located in {location}. The hotel has the following details: \n"
                "- Hotel ID: {hotel_id}\n"
                "- Price: {price}\n"
                "- Rating: {rating}\n"
                "- Address: {address}\n"
                "- Coordinates: Latitude: {latitude}, Longitude: {longitude}\n"
                "- Room Type: {room_type}\n"
                "Please make the title creative, engaging, and SEO-friendly, "
                "considering the amenities and features listed above."
                "The title should be different from {property_title}. Only give me the new title. Gon't Give any option. Just create a new title and return it."
            )

            # Initialize the model
            model = self.setup_model(self.API_KEY)

            # Iterate through each row and send the property_title to API
            for row in rows:
                id = row[0]
                location = row[1]
                property_title = row[2]
                hotel_id = row[3]
                price = row[4]
                rating = row[5]
                address = row[6]
                latitude = row[7]
                longitude = row[8]
                room_type = row[9]

                # Prepare the prompt using the hardcoded template with the new data
                prompt = prompt_template.format(
                    property_title=property_title,
                    location=location,
                    hotel_id=hotel_id,
                    price=price,
                    rating=rating,
                    address=address,
                    latitude=latitude,
                    longitude=longitude,
                    room_type=room_type
                )

                # Generate text using the model
                generated_title = self.generate_text(
                    model,
                    prompt,
                    max_tokens=256,
                    temperature=0.7
                )
                
                # Add a small delay between requests to avoid rate limiting
                sleep(1)

                # Output the hotel info with regenerated title
                self.stdout.write(self.style.SUCCESS(
                    f"ID: {id}, Hotel ID: {hotel_id}, Original Title: {property_title}, "
                    f"Generated Title: {generated_title}, Location: {location}, "
                    f"Price: {price}, Rating: {rating}, Address: {address}, "
                    f"Latitude: {latitude}, Longitude: {longitude}, Room Type: {room_type}"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
