from django.db import models

class RegeneratedPropertyTitle(models.Model):
    hotel_id = models.IntegerField()
    location = models.CharField(max_length=255, blank=True, null=True)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    regenerated_title = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    room_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Regenerated Title for Hotel {self.hotel_id} - {self.regenerated_title}"
    
class Description(models.Model):
    hotel_id = models.IntegerField()  # To associate the description with a specific hotel
    description = models.TextField(blank=True, null=True)  # Optional field for the description

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
