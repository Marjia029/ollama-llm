import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from django.core.management import call_command, CommandError
from django.db import connections
from property.models import TitleAndDescription
from datetime import datetime, timedelta
import logging

@patch('google.generativeai.GenerativeModel')
class GenerateTitleAndDescriptionCommandTests(TestCase):
    databases = {'default', 'trip_db'}
    
    def setUp(self):
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchall.return_value = [
            (1, "New York", "Test Hotel1", 123, "200", "4.5", "123 Main St", "40.7", "-74.0", "Deluxe Suite")
        ]
        self.mock_connection = MagicMock()
        self.mock_connection.cursor.return_value.__enter__.return_value = self.mock_cursor

    @patch('property.management.commands.generate_title_and_description.connections')
    def test_command_execution(self, mock_connections, mock_model):
        """Test the basic execution of the command"""
        # Create mock content response
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_model_instance.generate_content.side_effect = [
            MagicMock(text='Regenerated Title 1'),
            MagicMock(text='Regenerated Description 1'),
            # MagicMock(text='Regenerated Title 2'),
            # MagicMock(text='Regenerated Description 2'),
        ]
        
        # Set up the mock connection
        mock_connections.__getitem__.return_value = self.mock_connection
        
        call_command('generate_title_and_description')

        # Verify that a Summary instance exists
        title_and_description = TitleAndDescription.objects.filter(hotel_id=123).first()
        self.assertIsNotNone(title_and_description)
        self.assertEqual(title_and_description.hotel_id, 123)
        self.assertEqual(title_and_description.regenerated_title, "Regenerated Title 1")
