from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "country", "deadline", "status", "is_verified", "is_featured", "created_at")
    list_filter = ("type", "status", "country", "is_verified", "is_featured", "remote")
    search_fields = ("title", "organization", "country", "tags")
    ordering = ("-created_at",)
