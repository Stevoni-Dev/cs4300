#!/usr/bin/env python
"""Project entry point for Django management commands.

This module bootstraps the application and allows standard Django commands such as
``manage.py migrate`` and ``manage.py runserver`` to execute correctly.
"""

import os
import sys


def main() -> None:
    """Configure the Django settings module and run the requested command."""
    # Point Django at the project settings module before any management command runs.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
