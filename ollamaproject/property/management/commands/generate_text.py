import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import CommandError


class Command(BaseCommand):
    help = 'Generate text using Google Gemini AI model'

    def add_arguments(self, parser):
        help = 'Generate text using Google Gemini AI model'
        # Remove the '--api-key' argument to make it hardcoded or ask interactively
        # parser.add_argument(
        #     '--prompt',
        #     type=str,
        #     help='The prompt for text generation',
        #     default="Write a short story about a magical library"  # Default prompt
        # )
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

    def setup_model(self):
        """Configure and return the Gemini model"""
        try:
            # Use the hardcoded API key
            api_key = "AIzaSyBsiGjUOf5qbyylbqiYDokWhrGAlqpz7cw"
            genai.configure(api_key=api_key)
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

        prompt = "What is the Capital of Bangladesh?"
        # Setup model
        model = self.setup_model()

        # Generate text
        self.stdout.write(self.style.SUCCESS('Generating text...'))
        self.stdout.write('-' * 50)
        
        response = self.generate_text(
            model,
            prompt,
            options['max_tokens'],
            options['temperature']
        )
        
        self.stdout.write(response)
        self.stdout.write('-' * 50)
        self.stdout.write(self.style.SUCCESS('Text generation complete!'))
