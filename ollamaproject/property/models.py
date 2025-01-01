from django.db import models
from django.core.exceptions import ValidationError
    
class TitleAndDescription(models.Model):
    hotel_id = models.IntegerField()  # To associate the description with a specific hotel
    original_title = models.TextField(blank=True, null=True) # To associate the description with a specific
    regenerated_title = models.TextField(blank=True, null=True)  # To associate the description with a specific
    description = models.TextField(blank=True, null=True)  # Optional field for the description

    class Meta:
        verbose_name = "Title And Description"  # Singular form of the model name
        verbose_name_plural = "Titles And Descriptions"  # Plural form of the model name

    def __str__(self):
        return f"Description for Hotel ID: {self.hotel_id}"
    

class Summary(models.Model):
    hotel_id = models.IntegerField()  # To associate the description with a specific hotel
    summary = models.TextField(blank=True, null=True)  # Optional field for the description

    class Meta:
        verbose_name = "Summary"  # Singular form of the model name
        verbose_name_plural = "Summaries"  # Plural form of the model name

    def __str__(self):
        return f"Summary for Hotel ID: {self.hotel_id}"
    

class RatingAndReview(models.Model):
    hotel_id = models.IntegerField(unique=True)
    rating = models.FloatField()
    review = models.TextField()

    class Meta:
        db_table = 'property_ratingandreview'
        verbose_name = 'Rating and Review'
        verbose_name_plural = 'Ratings and Reviews'

    def __str__(self):
        return f"Hotel {self.hotel_id} - Rating: {self.rating}"

    def clean(self):
        # Ensure rating is between 1 and 5
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('Rating must be between 1 and 5')
