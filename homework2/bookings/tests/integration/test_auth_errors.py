"""Integration checks for the shared auth error contract."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings")

import django
import pytest


django.setup()

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIClient

from bookings.tests import tag


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """Test-only protected endpoint used to validate the auth contract."""
    return Response({"ok": True})


urlpatterns = [
    path("test-protected/", protected_view, name="test-protected"),
]


@tag("integration")
@pytest.mark.django_db
class TestAuthErrors:
    """Exercise the shared anonymous/CSRF auth failure contract."""

    @override_settings(ROOT_URLCONF=__name__)
    def test_anonymous_request_returns_401_with_shared_error_shape(self):
        client = APIClient()

        response = client.get("/test-protected/")

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    @override_settings(ROOT_URLCONF=__name__)
    def test_authenticated_invalid_csrf_request_returns_403(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="csrf-user",
            password="secret-passphrase",
        )
        client = APIClient(enforce_csrf_checks=True)
        client.force_authenticate(user=user)

        response = client.get("/test-protected/")

        assert response.status_code == 403
        assert response.json().keys() == {"detail"}
        assert response.json()["detail"].startswith("CSRF Failed:")
