import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.db import connections
from time import sleep
from django.core.management import CommandError
from property.models import Description

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for title and description regeneration'
    
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
            with connections['default'].cursor() as cursor:
                cursor.execute('TRUNCATE TABLE property_description RESTART IDENTITY CASCADE;')
            
            self.stdout.write(self.style.SUCCESS('Successfully truncated the table and reset IDs.'))

            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            # Updated prompt templates for both title and description
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

            model = self.setup_model(self.API_KEY)

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

                # Generate both title and description
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

                regenerated_title = self.generate_text(
                    model,
                    title_prompt,
                    max_tokens=256,
                    temperature=0.7
                )
                
                sleep(1)  # Delay between requests

                regenerated_description = self.generate_text(
                    model,
                    description_prompt,
                    max_tokens=512,  # Increased max tokens for longer description
                    temperature=0.7
                )
                
                sleep(1)  # Delay between requests

                # Save the regenerated data to the database
                regenerated_title_instance = Description(
                    hotel_id=hotel_id,
                    original_title=property_title,
                    regenerated_title=regenerated_title,
                    description=regenerated_description 
                    
                )
                regenerated_title_instance.save()

                # Output the hotel info with regenerated content
                self.stdout.write(self.style.SUCCESS(
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
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))