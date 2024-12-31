# yourapp/management/commands/generate_text.py

import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import CommandError

class Command(BaseCommand):
    help = 'Generate text using Google Gemini AI model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prompt',
            type=str,
            required=True,
            help='The prompt for text generation'
        )
        parser.add_argument(
            '--max-tokens',
            type=int,
            default=512,
            help='Maximum number of tokens to generate'
        )
        parser.add_argument(
            '--temperature',
            type=float,
            default=0.7,
            help='Temperature for text generation (0.0 to 1.0)'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            required=True,
            help='Google API key'
        )

    def setup_model(self, api_key):
        """Configure and return the Gemini model"""
        try:
            genai.configure(api_key="AIzaSyBsiGjUOf5qbyylbqiYDokWhrGAlqpz7cw")
            return genai.GenerativeModel('gemini-2.0-flash-exp')
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

    def handle(self, *args, **options):
        # Setup model
        model = self.setup_model(options['api_key'])

        # Generate text
        self.stdout.write(self.style.SUCCESS('Generating text...'))
        self.stdout.write('-' * 50)
        
        response = self.generate_text(
            model,
            options['prompt'],
            options['max_tokens'],
            options['temperature']
        )
        
        self.stdout.write(response)
        self.stdout.write('-' * 50)
        self.stdout.write(self.style.SUCCESS('Text generation complete!'))