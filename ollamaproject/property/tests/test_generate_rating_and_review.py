import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from django.core.management import call_command, CommandError
from django.db import connections
from property.models import RatingAndReview
from datetime import datetime, timedelta
import logging

@patch('google.generativeai.GenerativeModel')
class GenerateRatingAndReviewCommandTests(TestCase):
    databases = {'default', 'trip_db'}
    
    def setUp(self):
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchall.return_value = [
            (1, "New York", "Test Hotel", 123, "200", 4.5, "123 Main St", "40.7", "-74.0", "Deluxe Suite")
        ]
        self.mock_connection = MagicMock()
        self.mock_connection.cursor.return_value.__enter__.return_value = self.mock_cursor

    @patch('property.management.commands.generate_rating_and_review.connections')
    def test_command_execution(self, mock_connections, mock_model):
        """Test the basic execution of the command"""
        # Create mock content response
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_model_instance.generate_content.side_effect = [
            MagicMock(text='4.2'),
            MagicMock(text='Generated Review')
            # MagicMock(text='Regenerated Title 2'),
            # MagicMock(text='Regenerated Description 2'),
        ]
        
        # Set up the mock connection
        mock_connections.__getitem__.return_value = self.mock_connection
        
        call_command('generate_rating_and_review')

        # Verify that a Summary instance exists
        rating_and_review = RatingAndReview.objects.filter(hotel_id=123).first()
        self.assertIsNotNone(rating_and_review)
        self.assertEqual(rating_and_review.hotel_id, 123)
        self.assertEqual(rating_and_review.rating, 4.2)
        self.assertEqual(rating_and_review.review, 'Generated Review')
