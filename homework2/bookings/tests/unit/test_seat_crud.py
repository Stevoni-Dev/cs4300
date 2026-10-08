"""Unit tests for seat serializer validation and booking protection."""

import pytest
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError

from bookings.models import Booking, Movie, Seat
from bookings.serializers import SeatSerializer


User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestSeatCrud:
    """Validate seat labels, server-owned values, and deletion rules."""

    @pytest.fixture
    def movies(self):
        """Create separate inventories for uniqueness-scope checks."""
        first = Movie.objects.create(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2016-11-11",
            duration=116,
        )
        second = Movie.objects.create(
            title="Moonlight",
            description="A coming-of-age drama.",
            release_date="2016-10-21",
            duration=111,
        )
        return first, second

    def test_seat_number_is_required_trimmed_and_bounded(self, movies):
        """Creation rejects missing, blank, non-string, or long labels."""
        first_movie, _ = movies
        invalid_payloads = [
            {},
            {"movie": first_movie.pk, "seat_number": "  "},
            {"movie": first_movie.pk, "seat_number": "A" * 11},
            {"movie": first_movie.pk, "seat_number": 123},
        ]

        for payload in invalid_payloads:
            serializer = SeatSerializer(data=payload)
            assert not serializer.is_valid()
            assert "seat_number" in serializer.errors

        missing_movie = SeatSerializer(data={"seat_number": "A1"})
        assert not missing_movie.is_valid()
        assert "movie" in missing_movie.errors

        valid = SeatSerializer(
            data={"movie": first_movie.pk, "seat_number": " A1 "}
        )
        assert valid.is_valid(), valid.errors
        assert valid.validated_data["seat_number"] == "A1"

    def test_seat_number_uniqueness_is_scoped_to_movie(self, movies):
        """Duplicates fail with a field error, but another movie may reuse it.
        """
        first_movie, second_movie = movies
        existing = Seat.objects.create(movie=first_movie, seat_number="A1")

        duplicate = SeatSerializer(
            data={"movie": first_movie.pk, "seat_number": "A1"}
        )
        assert not duplicate.is_valid()
        assert "seat_number" in duplicate.errors

        same_number_elsewhere = SeatSerializer(
            data={"movie": second_movie.pk, "seat_number": "A1"}
        )
        assert same_number_elsewhere.is_valid(), same_number_elsewhere.errors
        same_number_elsewhere.save()

        rename_to_current_number = SeatSerializer(
            existing,
            data={"seat_number": "A1"},
            partial=True,
        )
        assert rename_to_current_number.is_valid(), (
            rename_to_current_number.errors
        )

    def test_status_is_available_and_movie_is_create_only(self, movies):
        """Writes cannot forge reservation state or move existing inventory."""
        first_movie, second_movie = movies
        create = SeatSerializer(
            data={
                "movie": first_movie.pk,
                "seat_number": "A1",
                "status": Seat.STATUS_RESERVED,
            }
        )
        assert create.is_valid(), create.errors
        seat = create.save()
        assert seat.status == Seat.STATUS_AVAILABLE

        update = SeatSerializer(
            seat,
            data={
                "movie": second_movie.pk,
                "seat_number": "A2",
                "status": Seat.STATUS_RESERVED,
            },
            partial=True,
        )
        assert update.is_valid(), update.errors
        update.save()
        seat.refresh_from_db()
        assert seat.movie == first_movie
        assert seat.seat_number == "A2"
        assert seat.status == Seat.STATUS_AVAILABLE

    def test_booked_seat_cannot_be_deleted(self, movies):
        """Booking protection keeps the seat and its history intact."""
        first_movie, _ = movies
        seat = Seat.objects.create(movie=first_movie, seat_number="A1")
        user = User.objects.create_user(
            username="seat-history-owner",
            password="valid-password-123",
        )
        booking = Booking.objects.create(
            movie=first_movie,
            seat=seat,
            user=user,
        )

        with pytest.raises(ProtectedError):
            seat.delete()

        assert Seat.objects.filter(pk=seat.pk).exists()
        assert Booking.objects.filter(pk=booking.pk).exists()
