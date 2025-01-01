from django.contrib import admin
from .models import *

@admin.register(RegeneratedPropertyTitle)
class RegeneratedPropertyTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'original_title', 'regenerated_title', 'rating', 'created_at')


@admin.register(Description)
class DescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'original_title', 'regenerated_title', 'description')


@admin.register(Summary)
class DescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'summary')


@admin.register(RatingAndReview)
class RatingAndReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'rating', 'review')
    list_filter = ('rating',)
    search_fields = ('hotel_id', 'review')
    ordering = ('id',)