"""Configuration for the bookings Django application."""

from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """App configuration for the movie-theater booking domain."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "bookings"
