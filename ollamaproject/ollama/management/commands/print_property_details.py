import requests
from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Fetch hotels data from trip_db and send property_title to Ollama for title regeneration'

    def handle(self, *args, **kwargs):
        # Connect to the trip_db and fetch the hotel data
        with connections['trip_db'].cursor() as cursor:
            cursor.execute("SELECT * FROM hotels;")
            rows = cursor.fetchall()
        
        # Iterate through each row and send the property_title to Ollama
        for row in rows:
            hotel_id = row[0]
            location = row[1]  # Assuming the title is in the second column
            property_title = row[2]  # Assuming location is in the third column
            description = row[3]  # Assuming description is in the fourth column (if exists)

            # Formatting the input for better title generation
            enhanced_input = f"Generate a catchy and SEO-friendly title for a hotel named '{property_title}' located in {location}. The hotel offers amenities like {description}. Make the title creative and engaging for potential guests."

            # Sending the enhanced input to Ollama API for regeneration
            ollama_url = 'http://ollama:11434/api/generate'  # Updated Ollama API URL
            data = {
                'input': enhanced_input
            }

            try:
                response = requests.post(ollama_url, json=data)
                response.raise_for_status()  # Raise an exception for error responses
                generated_title = response.json().get('generated_title', property_title)  # Default to original title if not found
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Error connecting to Ollama: {e}"))
                generated_title = property_title  # If Ollama fails, keep the original title
            
            # Output the hotel info with regenerated title
            self.stdout.write(self.style.SUCCESS(f"Hotel ID: {hotel_id}, Original Title: {property_title}, "
                                                 f"Generated Title: {generated_title}, Location: {location}, "
                                                 f"Description: {description}"))
