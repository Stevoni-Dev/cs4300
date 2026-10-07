"""Integration checks for DRF's configured authentication behavior."""

import os

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIClient

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "movie_theater_booking.settings",
)
django.setup()


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def protected_view(_request):
    """Test-only protected endpoint used to validate the auth contract."""
    return Response({"ok": True})


urlpatterns = [
    path("test-protected/", protected_view, name="test-protected"),
]


@pytest.mark.integration
@pytest.mark.django_db
class TestAuthErrors:
    """Exercise the configured SessionAuthentication behavior."""

    @override_settings(ROOT_URLCONF=__name__)
    def test_anonymous_request_uses_default_drf_authentication_response(
        self,
    ):
        """Anonymous SessionAuthentication requests have no challenge."""
        client = APIClient()

        response = client.get("/test-protected/")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }
        assert "WWW-Authenticate" not in response

    @override_settings(ROOT_URLCONF=__name__)
    def test_session_authentication_rejects_invalid_csrf(self):
        """SessionAuthentication denies unsafe requests without valid CSRF."""
        user_model = get_user_model()
        user_model.objects.create_user(
            username="csrf-user",
            password="secret-passphrase",
        )
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="csrf-user", password="secret-passphrase")

        response = client.post(
            "/test-protected/",
            {"hello": "world"},
        )

        assert response.status_code == 403
        assert response.json().keys() == {"detail"}
        assert response.json()["detail"].startswith("CSRF Failed:")
