import requests
import json
from django.core.management.base import BaseCommand
from django.db import connections
from time import sleep

class Command(BaseCommand):
    help = 'Fetch hotel data from trip_db and use Google Gemini API for title regeneration'
    
    # Correct endpoint for text-bison model
    API_URL = "https://api.generativeai.google.com/v1/models/text-bison:generate"
    API_KEY = "AIzaSyBsiGjUOf5qbyylbqiYDokWhrGAlqpz7cw"

    def handle(self, *args, **kwargs):
        try:
            # Connect to the trip_db and fetch the hotel data
            with connections['trip_db'].cursor() as cursor:
                cursor.execute("SELECT * FROM hotels;")
                rows = cursor.fetchall()

            # Iterate through each row and send the property_title to API
            for row in rows:
                hotel_id = row[0]
                location = row[1]
                property_title = row[2]
                description = row[3]

                # Prepare the prompt for better title generation
                prompt = (
                    f"Generate a catchy and SEO-friendly title for a hotel named '{property_title}' "
                    f"located in {location}. The hotel offers amenities like {description}. "
                    "Make the title creative and engaging for potential guests."
                )

                # Correct payload structure for text-bison model
                payload = {
                    "prompt": {
                        "text": prompt
                    },
                    "temperature": 0.7,
                    "maxOutputTokens": 256,
                    "topK": 40,
                    "topP": 0.8,
                }

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.API_KEY}"
                }

                try:
                    # Send the request to the API with proper timeout and SSL verification
                    response = requests.post(
                        self.API_URL,
                        json=payload,
                        headers=headers,
                        timeout=30,
                        verify=True
                    )
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        response_data = response.json()
                        generated_title = response_data.get('candidates', [{}])[0].get('output', property_title)
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"API returned status code {response.status_code}: {response.text}"
                        ))
                        generated_title = property_title

                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"Error connecting to API: {str(e)}"))
                    generated_title = property_title
                
                # Add a small delay between requests to avoid rate limiting
                sleep(1)

                # Output the hotel info with regenerated title
                self.stdout.write(self.style.SUCCESS(
                    f"Hotel ID: {hotel_id}, Original Title: {property_title}, "
                    f"Generated Title: {generated_title}, Location: {location}, "
                    f"Description: {description}"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))