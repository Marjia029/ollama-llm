from django.contrib import admin
from .models import RegeneratedPropertyTitle

@admin.register(RegeneratedPropertyTitle)
class RegeneratedPropertyTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_id', 'original_title', 'regenerated_title', 'rating', 'created_at')
