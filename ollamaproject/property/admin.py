from django.contrib import admin
from .models import *

@admin.register(RegeneratedPropertyTitle)
class RegeneratedPropertyTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'original_title', 'regenerated_title', 'rating', 'created_at')


@admin.register(Description)
class DescriptionAdmin(admin.ModelAdmin):
    list_display = ('hotel_id', 'description')


@admin.register(Summary)
class DescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'summary')