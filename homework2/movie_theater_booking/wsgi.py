"""WSGI configuration for the project.

This module creates the WSGI application used by Gunicorn and other standard web servers
in production and local execution.
"""

import os

from django.core.wsgi import get_wsgi_application

# Register the project settings module before the WSGI application starts serving
# requests.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings")

application = get_wsgi_application()
