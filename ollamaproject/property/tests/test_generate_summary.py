import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from django.core.management import call_command, CommandError
from django.db import connections
from property.models import Summary
from datetime import datetime, timedelta
import logging

@patch('google.generativeai.GenerativeModel')
class GenerateSummaryCommandTests(TestCase):
    databases = {'default', 'trip_db'}
    
    def setUp(self):
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchall.return_value = [
            (1, "New York", "Test Hotel", 123, "200", "4.5", "123 Main St", "40.7", "-74.0", "Deluxe Suite")
        ]
        self.mock_connection = MagicMock()
        self.mock_connection.cursor.return_value.__enter__.return_value = self.mock_cursor

    @patch('property.management.commands.generate_summary.connections')
    def test_command_execution(self, mock_connections, mock_genai):
        """Test the basic execution of the command"""
        # Create mock content response
        mock_content_response = MagicMock()
        mock_content_response.text = "Generated summary text"
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_content_response
        mock_genai.return_value = mock_model
        
        # Set up the mock connection
        mock_connections.__getitem__.return_value = self.mock_connection
        
        call_command('generate_summary')

        # Verify that a Summary instance exists
        summary = Summary.objects.filter(hotel_id=123).first()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.hotel_id, 123)
        self.assertEqual(summary.summary, "Generated summary text")
