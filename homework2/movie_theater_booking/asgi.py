"""ASGI configuration for the project.

This application object is required when Django runs under an ASGI server or
other tooling that uses the asynchronous server interface.
"""

import os

from django.core.asgi import get_asgi_application

# Load project settings before creating the ASGI application.
os.environ.setdefault(
	"DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings"
)

application = get_asgi_application()
