"""Integration checks for authentication on real protected API routes."""

# Django adds ORM managers dynamically; Pylint cannot infer these attributes.
# pylint: disable=no-member

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookings.models import Movie


User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
def test_movie_writes_reject_authenticated_session_without_csrf():
    """DRF rejects session-authenticated movie writes without valid CSRF."""
    user = User.objects.create_user(
        username="csrf-movie-writer",
        password="secret-passphrase",
    )
    movie = Movie.objects.create(
        title="Protected Movie",
        description="A movie used to verify write protection.",
        release_date="2026-10-08",
        duration=100,
    )
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)

    create_response = client.post(
        "/api/movies/",
        {
            "title": "CSRF Created Movie",
            "description": "This write must be rejected.",
            "release_date": "2026-10-09",
            "duration": 101,
        },
        format="json",
    )
    update_response = client.patch(
        f"/api/movies/{movie.pk}/",
        {"title": "CSRF Updated Movie"},
        format="json",
    )
    delete_response = client.delete(f"/api/movies/{movie.pk}/")

    assert all(
        response.status_code >= 400
        for response in (create_response, update_response, delete_response)
    )
    assert not Movie.objects.filter(title="CSRF Created Movie").exists()
    movie.refresh_from_db()
    assert movie.title == "Protected Movie"
