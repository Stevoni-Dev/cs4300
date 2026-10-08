# pylint: disable=duplicate-code
"""Django settings for the movie theater booking project.

These settings centralize environment configuration, installed apps, database
selection, template rendering, and static-file behavior.
"""

from __future__ import annotations

import os
from pathlib import Path

# Use PostgreSQL on Render and SQLite locally when DATABASE_URL is not set.
try:
    import dj_database_url
except ImportError:  # pragma: no cover - dependency is optional until installation
    dj_database_url = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - provided by the optional dev dependencies
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent.parent

# Load local settings first; production uses hosting environment variables.
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.is_file() and load_dotenv is not None:
    load_dotenv(ENV_FILE, override=False)

# Production deployments should explicitly set these values in the environment.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.environ.get("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,testserver"
    ).split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://0.0.0.0:3000",
    ).split(",")
    if origin.strip()
]
if DEBUG and "https://*.lab.devedu.io" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("https://*.lab.devedu.io")

# Include Django auth, messaging, static files, DRF, Bootstrap, and the app.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "rest_framework",
    "behave_django",
    "bookings.apps.BookingsConfig",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Middleware order controls sessions, CSRF checks, and request processing.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "movie_theater_booking.urls"

# Configure templates for server-rendered pages alongside API views.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "bookings" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "movie_theater_booking.wsgi.application"
ASGI_APPLICATION = "movie_theater_booking.asgi.application"

# Prefer Render's PostgreSQL URL; otherwise use local SQLite for development.
if dj_database_url is not None:
    DATABASES = {
        "default": dj_database_url.config(
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Collect static assets into one folder for deployment and local use.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Shared message storage works with Bootstrap alert rendering in forms.
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
