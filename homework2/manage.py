#!/usr/bin/env python
"""Project entry point for Django management commands.

This module bootstraps the application and allows standard Django commands
such as ``manage.py migrate`` and ``manage.py runserver`` to execute correctly.
"""

import os
import sys
from django.core.management import execute_from_command_line


def main() -> None:
    """Configure the Django settings module and run the requested command."""
    # Set the project settings module before running a management command.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings"
    )
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
