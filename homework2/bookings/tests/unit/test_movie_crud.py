"""Unit tests for movie catalog validation and booking protection."""

import pytest
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError

from bookings.models import Booking, Movie, Seat
from bookings.serializers import MovieSerializer


User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestMovieCrud:
    """Validate movie fields, partial updates, and booking preservation."""

    @pytest.fixture
    def movie(self):
        """Create a valid movie for update and deletion tests."""
        return Movie.objects.create(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2016-11-11",
            duration=116,
        )

    def test_movie_serializer_requires_fields_and_validates_values(self):
        """Creation rejects missing or invalid movie field values."""
        missing_fields = MovieSerializer(data={})
        assert not missing_fields.is_valid()
        assert {"title", "description", "release_date", "duration"} <= set(
            missing_fields.errors
        )

        invalid_fields = MovieSerializer(
            data={
                "title": "   ",
                "description": "   ",
                "release_date": "not-a-date",
                "duration": 0,
            }
        )
        assert not invalid_fields.is_valid()
        assert {"title", "description", "release_date", "duration"} <= set(
            invalid_fields.errors
        )

    def test_partial_update_validates_provided_fields_only(self, movie):
        """PATCH may update one field but rejects invalid supplied values."""
        valid_patch = MovieSerializer(
            movie,
            data={"title": "Arrival: Revised"},
            partial=True,
        )
        assert valid_patch.is_valid(), valid_patch.errors
        valid_patch.save()
        movie.refresh_from_db()
        assert movie.title == "Arrival: Revised"
        assert movie.description == "A linguist decodes a mysterious signal."

        invalid_patch = MovieSerializer(
            movie,
            data={"duration": 0},
            partial=True,
        )
        assert not invalid_patch.is_valid()
        assert "duration" in invalid_patch.errors

    def test_movie_with_booking_cannot_be_deleted(self, movie):
        """Database relations protect a movie referenced by booking history."""
        seat = Seat.objects.create(movie=movie, seat_number="A1")
        user = User.objects.create_user(
            username="crud-history-owner",
            password="valid-password-123",
        )
        Booking.objects.create(movie=movie, seat=seat, user=user)

        with pytest.raises(ProtectedError):
            movie.delete()

        assert Movie.objects.filter(pk=movie.pk).exists()
