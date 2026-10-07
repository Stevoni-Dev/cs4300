"""Smoke-step definitions for the Behave-Django test harness."""

from __future__ import annotations

from behave import given, then
from django.conf import settings


@given("the Django app is ready")
def step_django_app_ready(context):
    """Assert the app is configured to serve the Django settings module."""
    assert settings.configured is True


@then("the settings module is configured")
def step_settings_module_configured(context):
    """Verify the Django settings module was loaded and usable."""
    assert settings.configured is True
    assert "default" in settings.DATABASES
    assert "ENGINE" in settings.DATABASES["default"]
