from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.test import TransactionTestCase
from property.models import TitleAndDescription
from django.db import connection, connections

class CommandTest(TransactionTestCase):
    databases = {'default', 'trip_db'}

    def setUp(self):
        TitleAndDescription.objects.all().delete()
        self.mock_hotel_data = [
            (1, "New York", "Hotel Sunshine", "H123", "100", 4.5, "123 Main St", 40.7128, -74.0060, "Deluxe")
        ]
        
        # Mock responses for both title and description
        self.mock_title_response = MagicMock()
        self.mock_title_response.text = "Regenerated Hotel Title"
        
        self.mock_desc_response = MagicMock()
        self.mock_desc_response.text = "Regenerated Hotel Description"

    def mock_generate_content(self, prompt, generation_config=None):
        """Helper to return different responses based on the prompt"""
        if "title" in prompt.lower():
            return self.mock_title_response
        return self.mock_desc_response

    @patch('property.management.commands.generate_title_and_description.GEMINI_API_KEY', 'fake-key')
    @patch('property.management.commands.generate_title_and_description.Command.generate_text_with_retry')
    @patch('property.management.commands.generate_title_and_description.connections')
    def test_command_success(self, mock_connections, mock_generate_text):
        # Mock the database connections
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchall.return_value = self.mock_hotel_data
        mock_connections['trip_db'].cursor.return_value = mock_cursor
        
        mock_default_cursor = MagicMock()
        mock_connections['default'].cursor.return_value = mock_default_cursor
        mock_connections['default'].ops.sequence_reset_sql.return_value = []

        # Mock the text generation to return different values for title and description
        mock_generate_text.side_effect = ["Regenerated Hotel Title", "Regenerated Hotel Description"]
        
        # Run the command
        call_command('generate_title_and_description')
        
        # Verify the results
        self.assertEqual(TitleAndDescription.objects.count(), 1)
        td = TitleAndDescription.objects.first()
        self.assertEqual(td.regenerated_title, "Regenerated Hotel Title")
        self.assertEqual(td.description, "Regenerated Hotel Description")
        self.assertEqual(td.hotel_id, "H123")

    @patch('property.management.commands.generate_title_and_description.GEMINI_API_KEY', 'fake-key')
    @patch('property.management.commands.generate_title_and_description.Command.generate_text_with_retry')
    @patch('property.management.commands.generate_title_and_description.connections')
    def test_command_error_handling(self, mock_connections, mock_generate_text):
        # Mock the database connections
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchall.return_value = self.mock_hotel_data
        mock_connections['trip_db'].cursor.return_value = mock_cursor
        
        mock_default_cursor = MagicMock()
        mock_connections['default'].cursor.return_value = mock_default_cursor
        mock_connections['default'].ops.sequence_reset_sql.return_value = []

        # Setup the text generation to raise an exception
        mock_generate_text.side_effect = Exception("Test error")
        
        # Run the command and verify it raises the exception
        with self.assertRaises(Exception) as context:
            call_command('generate_title_and_description')
        
        self.assertEqual(str(context.exception), "Test error")

    @patch('property.management.commands.generate_title_and_description.GEMINI_API_KEY', 'fake-key')
    @patch('property.management.commands.generate_title_and_description.Command._handle_rate_limiting')
    @patch('property.management.commands.generate_title_and_description.Command.generate_text_with_retry')
    @patch('property.management.commands.generate_title_and_description.connections')
    def test_command_rate_limiting(self, mock_connections, mock_generate_text, mock_rate_limiting):
        # Mock the database connections
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchall.return_value = self.mock_hotel_data
        mock_connections['trip_db'].cursor.return_value = mock_cursor
        
        mock_default_cursor = MagicMock()
        mock_connections['default'].cursor.return_value = mock_default_cursor
        mock_connections['default'].ops.sequence_reset_sql.return_value = []

        # Mock the text generation
        mock_generate_text.side_effect = ["Regenerated Hotel Title", "Regenerated Hotel Description"]
        
        # Run the command
        call_command('generate_title_and_description')
        
        # Verify rate limiting was called
        # Since generate_text_with_retry is called twice (title and description),
        # rate_limiting should be called twice
        self.assertEqual(mock_rate_limiting.call_count, 2)

    def tearDown(self):
        TitleAndDescription.objects.all().delete()