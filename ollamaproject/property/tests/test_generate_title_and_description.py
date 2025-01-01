from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from property.models import TitleAndDescription

class GenerateTitleAndDescriptionTest(TestCase):
    databases = {'default', 'trip_db'}  # Allow access to both 'default' and 'trip_db'

    def setUp(self):
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchall.return_value = [
            (1, 'New York', 'Hotel Blue', 1234, 200, 4.5, '123 Main St', '40.7128', '-74.0060', 'Suite'),
            (2, 'San Francisco', 'Hotel Gold', 5678, 300, 4.8, '456 Market St', '37.7749', '-122.4194', 'Deluxe'),
        ]
        self.mock_connection = MagicMock()
        self.mock_connection.cursor.return_value.__enter__.return_value = self.mock_cursor

    @patch('google.generativeai.GenerativeModel')
    @patch('django.db.connections.__getitem__')
    def test_command_execution(self, mock_connections, mock_model):
        # Mock the external model's method
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_model_instance.generate_content.side_effect = [
            MagicMock(text='Regenerated Title 1'),
            MagicMock(text='Regenerated Description 1'),
            MagicMock(text='Regenerated Title 2'),
            MagicMock(text='Regenerated Description 2'),
        ]

        # Execute the management command
        call_command('generate_title_and_description')

        # Verify database updates
        entries = TitleAndDescription.objects.all()
        self.assertEqual(entries.count(), 2)

        # Check the first entry
        entry_1 = entries.get(hotel_id=1234)
        self.assertEqual(entry_1.original_title, 'Hotel Blue')
        self.assertEqual(entry_1.regenerated_title, 'Regenerated Title 1')
        self.assertEqual(entry_1.description, 'Regenerated Description 1')

        # Check the second entry
        entry_2 = entries.get(hotel_id=5678)
        self.assertEqual(entry_2.original_title, 'Hotel Gold')
        self.assertEqual(entry_2.regenerated_title, 'Regenerated Title 2')
        self.assertEqual(entry_2.description, 'Regenerated Description 2')

        # Confirm model method calls
        self.assertEqual(mock_model_instance.generate_content.call_count, 4)

        # Check the arguments used in API calls
        calls = mock_model_instance.generate_content.call_args_list
        self.assertIn('Generate a catchy and SEO-friendly title for a hotel', calls[0][0][0])
        self.assertIn('Write a compelling and detailed description for a hotel', calls[1][0][0])

        # Ensure logs contain progress information
        with open('generation_log.txt', 'r') as log_file:
            log_content = log_file.read()
            self.assertIn('Processing hotel 1 of 2', log_content)
            self.assertIn('Processing hotel 2 of 2', log_content)
