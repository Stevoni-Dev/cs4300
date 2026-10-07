"""Page integration tests for the movie browse flow."""

import pytest

from bookings.models import Movie, Seat


@pytest.mark.integration
@pytest.mark.django_db
class TestBrowsePages:
    """Assert the public movie browse views show the correct data."""

    def test_movie_listing_page_shows_movies(self, client):
        """The browse page should show available movies."""
        movie = Movie.objects.create(
            title="Dune",
            description="A noble family enters a dangerous desert planet.",
            release_date="2026-10-10",
            duration=155,
        )
        Seat.objects.create(movie=movie, seat_number="A1", status="available")

        response = client.get("/movies/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Dune" in content
        assert "available" in content.lower()

    def test_movie_detail_page_shows_seat_availability(self, client):
        """Choosing a movie should display the movie and seat states."""
        movie = Movie.objects.create(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2026-10-11",
            duration=116,
        )
        Seat.objects.create(movie=movie, seat_number="B4", status="available")
        Seat.objects.create(movie=movie, seat_number="B5", status="reserved")

        response = client.get(f"/movies/{movie.pk}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Arrival" in content
        assert "B4" in content
        assert "B5" in content
        assert "reserved" in content.lower()

    def test_empty_movie_listing_page_has_helpful_message(self, client):
        """A page with no movies should show an empty state."""
        response = client.get("/movies/")

        assert response.status_code == 200
        content = response.content.decode().lower()
        assert "no movies" in content or "empty" in content
