"""Unit tests for the movie and seat domain model rules."""

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Movie, Seat


@pytest.mark.unit
@pytest.mark.django_db
class TestMovieSeatModels:
    """Validate the model requirements for movie browsing and seat state."""

    def test_movie_requires_non_empty_title_description_and_date(self):
        """Movie fields should be required and must not be blank."""
        movie = Movie(
            title="",
            description="",
            release_date=None,
            duration=120,
        )

        with pytest.raises(ValidationError):
            movie.full_clean()

    def test_movie_duration_must_be_positive(self):
        """Movie duration should be a positive whole-minute value."""
        movie = Movie(
            title="Inception",
            description="A dream within a dream.",
            release_date="2026-10-07",
            duration=0,
        )

        with pytest.raises(ValidationError):
            movie.full_clean()

    def test_seat_status_choices_and_movie_seat_uniqueness(self):
        """Seat status should be constrained and seat numbers unique per movie."""
        movie = Movie(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2026-10-08",
            duration=116,
        )
        movie.full_clean()
        movie.save()

        available_seat = Seat(movie=movie, seat_number="A1", status="available")
        available_seat.full_clean()
        available_seat.save()

        reserved_seat = Seat(movie=movie, seat_number="A1", status="reserved")
        with pytest.raises(ValidationError):
            reserved_seat.full_clean()

        invalid_state = Seat(movie=movie, seat_number="A2", status="sold")
        with pytest.raises(ValidationError):
            invalid_state.full_clean()
