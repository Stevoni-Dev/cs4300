"""Django settings for the movie theater booking project.

These settings centralize the environment configuration, installed apps, database
selection, template rendering, and static-file behavior for the application.
"""

from __future__ import annotations

import os
from pathlib import Path

# Allow the project to use a PostgreSQL configuration on Render while still defaulting
# to SQLite during local development when no DATABASE_URL is provided.
try:
    import dj_database_url
except ImportError:  # pragma: no cover - dependency is optional until installation
    dj_database_url = None


BASE_DIR = Path(__file__).resolve().parent.parent

# Development defaults are intentionally simple, but production deployments should set
# these values explicitly in the environment rather than hard-coding secrets.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.environ.get("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://0.0.0.0:3000",
    ).split(",")
    if origin.strip()
]

# The project includes Django's built-in auth, message framework, and the app itself.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bookings.apps.BookingsConfig",
]

# Middleware order matters for session handling, CSRF checks, and request processing.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "movie_theater_booking.urls"

# Templates are configured to support server-rendered pages alongside the API views.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# Prefer the Render PostgreSQL connection string when it exists; otherwise fall back to
# the local SQLite database for simple development and testing.
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
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static assets are collected into a single folder for deployment and local use.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
