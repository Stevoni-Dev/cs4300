"""Integration tests for authenticated movie catalog CRUD API behavior."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookings.models import Booking, Movie, Seat


User = get_user_model()


def _movie_data(title="Arrival"):
    """Return a valid movie payload for create and replace requests."""
    return {
        "title": title,
        "description": "A linguist decodes a mysterious signal.",
        "release_date": "2016-11-11",
        "duration": 116,
    }


@pytest.mark.integration
@pytest.mark.django_db
class TestMovieCrudApi:
    """Exercise public reads and authenticated movie CRUD operations."""

    @pytest.fixture
    def user(self):
        """Create a signed-in catalog editor account."""
        return User.objects.create_user(
            username="catalog-editor",
            password="valid-password-123",
        )

    @pytest.fixture
    def movie(self):
        """Create a movie for retrieve, update, and delete requests."""
        return Movie.objects.create(
            title="Existing Film",
            description="An existing movie for CRUD API tests.",
            release_date="2020-01-01",
            duration=100,
        )

    def test_signed_in_user_can_create_read_update_and_delete_movie(
        self, user
    ):
        """The complete CRUD flow updates the same public catalog record."""
        client = APIClient()
        client.force_login(user)

        create_response = client.post(
            "/api/movies/",
            _movie_data(),
            format="json",
        )
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        assert create_response.json()["title"] == "Arrival"

        detail_response = client.get(f"/api/movies/{movie_id}/")
        assert detail_response.status_code == 200
        assert detail_response.json()["description"] == (
            "A linguist decodes a mysterious signal."
        )

        replace_response = client.put(
            f"/api/movies/{movie_id}/",
            _movie_data(title="Arrival: Full Feature"),
            format="json",
        )
        assert replace_response.status_code == 200
        assert replace_response.json()["title"] == "Arrival: Full Feature"

        patch_response = client.patch(
            f"/api/movies/{movie_id}/",
            {"duration": 117},
            format="json",
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["duration"] == 117

        public_list = APIClient().get("/api/movies/")
        assert public_list.status_code == 200
        assert any(
            item["id"] == movie_id and item["title"] == "Arrival: Full Feature"
            for item in public_list.json()
        )

        delete_response = client.delete(f"/api/movies/{movie_id}/")
        assert delete_response.status_code == 204
        assert not Movie.objects.filter(pk=movie_id).exists()

    def test_anonymous_movie_writes_are_rejected(self, movie):
        """Anonymous create, update, and delete requests require sign-in."""
        client = APIClient()

        create_response = client.post(
            "/api/movies/",
            _movie_data(title="Anonymous Film"),
            format="json",
        )
        update_response = client.patch(
            f"/api/movies/{movie.pk}/",
            {"title": "Unauthorized Update"},
            format="json",
        )
        delete_response = client.delete(f"/api/movies/{movie.pk}/")

        assert create_response.status_code == 403
        assert update_response.status_code == 403
        assert delete_response.status_code == 403
        assert not Movie.objects.filter(title="Anonymous Film").exists()
        movie.refresh_from_db()
        assert movie.title == "Existing Film"

    def test_invalid_movie_fields_return_field_errors(self, user):
        """Invalid create and partial update values return 400 responses."""
        client = APIClient()
        client.force_login(user)

        invalid_create = client.post(
            "/api/movies/",
            {
                "title": " ",
                "description": "A description.",
                "release_date": "not-a-date",
                "duration": 0,
            },
            format="json",
        )
        assert invalid_create.status_code == 400
        assert {"title", "release_date", "duration"} <= set(
            invalid_create.json()
        )

        movie = Movie.objects.create(
            title="Patch target",
            description="A movie for invalid PATCH.",
            release_date="2020-01-01",
            duration=100,
        )
        invalid_patch = client.patch(
            f"/api/movies/{movie.pk}/",
            {"duration": 0},
            format="json",
        )
        assert invalid_patch.status_code == 400
        assert "duration" in invalid_patch.json()

    def test_unknown_movie_updates_and_deletes_return_not_found(self, user):
        """Writes to an unknown movie identifier return 404."""
        client = APIClient()
        client.force_login(user)

        update_response = client.patch(
            "/api/movies/999999/",
            {"title": "Missing"},
            format="json",
        )
        delete_response = client.delete("/api/movies/999999/")

        assert update_response.status_code == 404
        assert delete_response.status_code == 404

    def test_movie_with_booking_history_cannot_be_deleted(self, user, movie):
        """Deletion returns conflict and preserves catalog booking history."""
        seat = Seat.objects.create(movie=movie, seat_number="A1")
        Booking.objects.create(movie=movie, seat=seat, user=user)
        client = APIClient()
        client.force_login(user)

        response = client.delete(f"/api/movies/{movie.pk}/")

        assert response.status_code == 409
        movie.refresh_from_db()
        assert movie.title == "Existing Film"
        assert Booking.objects.filter(movie=movie).count() == 1
