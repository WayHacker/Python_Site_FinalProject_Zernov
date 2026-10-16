from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("ad", "author", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("ad__title", "author__username", "text")
    readonly_fields = ("created_at",)
