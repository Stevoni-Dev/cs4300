"""ASGI configuration for the project.

This application object is required by Django when running under an ASGI server such as
an async deployment environment or future tooling that uses the ASGI interface.
"""

import os

from django.core.asgi import get_asgi_application

# Ensure the Django project settings are loaded before the ASGI app is created.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings")

application = get_asgi_application()
