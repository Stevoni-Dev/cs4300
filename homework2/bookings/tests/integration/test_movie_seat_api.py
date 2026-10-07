"""Integration tests for the public movie and seat API."""

import pytest
from rest_framework.test import APIClient

from bookings.models import Movie, Seat


@pytest.mark.integration
@pytest.mark.django_db
class TestMovieSeatApi:
    """Exercise public movie and seat list/detail behavior."""

    @pytest.fixture
    def movie(self):
        movie = Movie.objects.create(
            title="Inception",
            description="A dream within a dream.",
            release_date="2026-10-07",
            duration=148,
        )
        Seat.objects.create(movie=movie, seat_number="A1", status="available")
        Seat.objects.create(movie=movie, seat_number="A2", status="reserved")
        return movie

    def test_public_movie_list_and_detail(self, movie):
        """Visitors should be able to read public movie listings and details."""
        client = APIClient()

        list_response = client.get("/api/movies/")
        assert list_response.status_code == 200
        assert list_response.json()

        detail_response = client.get(f"/api/movies/{movie.pk}/")
        assert detail_response.status_code == 200
        assert detail_response.json()["title"] == "Inception"

    def test_get_seats_requires_a_valid_movie_query(self, movie):
        """Seat list queries should validate the required movie identifier."""
        client = APIClient()

        missing_movie_response = client.get("/api/seats/")
        assert missing_movie_response.status_code == 400

        invalid_movie_response = client.get("/api/seats/", {"movie": "abc"})
        assert invalid_movie_response.status_code == 400

        unknown_movie_response = client.get("/api/seats/", {"movie": 999999})
        assert unknown_movie_response.status_code == 404

    def test_seat_list_for_movie_returns_only_that_movies_seats(self, movie):
        """The seat API should return only seats for the selected movie."""
        client = APIClient()

        response = client.get("/api/seats/", {"movie": movie.pk})
        assert response.status_code == 200
        seats = response.json()
        assert len(seats) == 2
        assert {seat["seat_number"] for seat in seats} == {"A1", "A2"}

        seat_detail_response = client.get(f"/api/seats/{seats[0]['id']}/")
        assert seat_detail_response.status_code == 200
        assert seat_detail_response.json()["seat_number"] == seats[0]["seat_number"]

    def test_empty_seat_list_for_a_movie_without_seats(self):
        """Movies without any seats should return an empty list."""
        movie = Movie.objects.create(
            title="The Matrix",
            description="A hacker learns the truth.",
            release_date="2026-10-09",
            duration=136,
        )
        client = APIClient()

        response = client.get("/api/seats/", {"movie": movie.pk})
        assert response.status_code == 200
        assert response.json() == []
