from django.test import TestCase
from django.core.exceptions import ValidationError
from property.models import TitleAndDescription, Summary, RatingAndReview

class TitleAndDescriptionTests(TestCase):
    def setUp(self):
        self.title_desc = TitleAndDescription.objects.create(
            hotel_id=1,
            original_title="Original Hotel Title",
            regenerated_title="Regenerated Hotel Title",
            description="A detailed description of the hotel"
        )

    def test_title_description_creation(self):
        """Test if TitleAndDescription model can be created with all fields"""
        self.assertEqual(self.title_desc.hotel_id, 1)
        self.assertEqual(self.title_desc.original_title, "Original Hotel Title")
        self.assertEqual(self.title_desc.regenerated_title, "Regenerated Hotel Title")
        self.assertEqual(self.title_desc.description, "A detailed description of the hotel")

    def test_title_description_str_method(self):
        """Test the string representation of TitleAndDescription model"""
        self.assertEqual(str(self.title_desc), "Description for Hotel ID: 1")

    def test_nullable_fields(self):
        """Test if optional fields can be null"""
        nullable_title_desc = TitleAndDescription.objects.create(
            hotel_id=2
        )
        self.assertIsNone(nullable_title_desc.original_title)
        self.assertIsNone(nullable_title_desc.regenerated_title)
        self.assertIsNone(nullable_title_desc.description)

class SummaryTests(TestCase):
    def setUp(self):
        self.summary = Summary.objects.create(
            hotel_id=1,
            summary="A brief summary of the hotel"
        )

    def test_summary_creation(self):
        """Test if Summary model can be created with all fields"""
        self.assertEqual(self.summary.hotel_id, 1)
        self.assertEqual(self.summary.summary, "A brief summary of the hotel")

    def test_summary_str_method(self):
        """Test the string representation of Summary model"""
        self.assertEqual(str(self.summary), "Summary for Hotel ID: 1")

    def test_nullable_summary_field(self):
        """Test if summary field can be null"""
        nullable_summary = Summary.objects.create(
            hotel_id=2
        )
        self.assertIsNone(nullable_summary.summary)

class RatingAndReviewTests(TestCase):
    def setUp(self):
        self.rating_review = RatingAndReview.objects.create(
            hotel_id=12345,
            rating=4.5,
            review="Great hotel with excellent service"
        )

    def test_rating_review_creation(self):
        """Test if RatingAndReview model can be created with all fields"""
        self.assertEqual(self.rating_review.hotel_id, 12345)
        self.assertEqual(self.rating_review.rating, 4.5)
        self.assertEqual(self.rating_review.review, "Great hotel with excellent service")

    def test_rating_review_str_method(self):
        """Test the string representation of RatingAndReview model"""
        self.assertEqual(str(self.rating_review), "Hotel 12345 - Rating: 4.5")

    def test_rating_validation(self):
        """Test rating validation for values outside the allowed range"""
        # Test rating below minimum
        with self.assertRaises(ValidationError):
            invalid_rating = RatingAndReview(
                hotel_id=45678,
                rating=0.5,
                review="Test review"
            )
            invalid_rating.full_clean()

        # Test rating above maximum
        with self.assertRaises(ValidationError):
            invalid_rating = RatingAndReview(
                hotel_id=78912,
                rating=5.5,
                review="Test review"
            )
            invalid_rating.full_clean()

    def test_hotel_id_unique_constraint(self):
        """Test that hotel_id must be unique"""
        with self.assertRaises(Exception):
            RatingAndReview.objects.create(
                hotel_id=12345,  # This hotel_id already exists from setUp
                rating=4.0,
                review="Another review"
            )