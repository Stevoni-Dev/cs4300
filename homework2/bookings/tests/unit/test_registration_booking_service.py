# pylint: disable=line-too-long
"""Unit tests for registration and atomic seat booking behavior."""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bookings.forms import RegistrationForm, SignInForm
from bookings.models import Booking, Movie, Seat
from bookings.services import create_booking


User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestRegistrationBookingService:
    """Check registration and reservation rules at their domain boundary."""

    @pytest.fixture
    def movie_and_seats(self):
        """Create one movie with two available seats."""
        movie = Movie.objects.create(
            title="Inception",
            description="A dream within a dream.",
            release_date="2026-10-07",
            duration=148,
        )
        first_seat = Seat.objects.create(movie=movie, seat_number="A1")
        second_seat = Seat.objects.create(movie=movie, seat_number="A2")
        return movie, first_seat, second_seat

    def test_registration_validates_required_and_matching_fields(self):
        """Registration identifies blank identifiers and invalid passwords."""
        missing_fields = RegistrationForm(
            data={"username": "", "password1": "", "password2": ""}
        )
        assert not missing_fields.is_valid()
        assert "username" in missing_fields.errors
        assert "password1" in missing_fields.errors

        mismatched_passwords = RegistrationForm(
            data={
                "username": "new-user",
                "password1": "valid-password-123",
                "password2": "different-password-456",
            }
        )
        assert not mismatched_passwords.is_valid()
        assert "password2" in mismatched_passwords.errors

    def test_duplicate_account_identifier_has_a_field_error(self):
        """An existing username is rejected as a username-specific error."""
        User.objects.create_user(username="existing-user", password="pass-123")
        form = RegistrationForm(
            data={
                "username": "existing-user",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
            }
        )

        assert not form.is_valid()
        assert "username" in form.errors

    def test_invalid_registration_creates_no_user(self):
        """Invalid registration data must not persist a partial account."""
        form = RegistrationForm(
            data={
                "username": "new-user",
                "password1": "valid-password-123",
                "password2": "different-password-456",
            }
        )

        assert not form.is_valid()
        assert not User.objects.filter(username="new-user").exists()

    @pytest.mark.parametrize(
        "credentials",
        [
            {"username": "unknown-user", "password": "valid-password-123"},
            {"username": "known-user", "password": "wrong-password-456"},
        ],
    )
    def test_failed_sign_in_has_generic_error_and_no_session(
        self, credentials
    ):
        """Unknown users and wrong passwords expose one failure."""
        User.objects.create_user(
            username="known-user",
            password="correct-pass-123",
        )
        form = SignInForm(data=credentials)

        assert not form.is_valid()
        assert form.non_field_errors()
        assert not form.get_user()
        assert "_auth_user_id" not in form.request.session

    def test_booking_claim_and_record_are_atomic(self, movie_and_seats):
        """A failed booking insert rolls back the seat claim."""
        movie, seat, _ = movie_and_seats
        user = User.objects.create_user(username="booker", password="pass-123")

        with patch.object(
            Booking.objects,
            "create",
            side_effect=IntegrityError("booking insert failed"),
        ):
            with pytest.raises(IntegrityError):
                create_booking(user=user, movie=movie, seat=seat)

        seat.refresh_from_db()
        assert seat.status == Seat.STATUS_AVAILABLE
        assert not Booking.objects.filter(seat=seat).exists()

    def test_booking_rejects_a_seat_from_another_movie(self, movie_and_seats):
        """A seat cannot be booked through a different movie identifier."""
        _, _, seat = movie_and_seats
        other_movie = Movie.objects.create(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2026-10-08",
            duration=116,
        )
        user = User.objects.create_user(
            username="booker",
            password="pass-123",
        )

        with pytest.raises(ValidationError):
            create_booking(user=user, movie=other_movie, seat=seat)

        seat.refresh_from_db()
        assert seat.status == Seat.STATUS_AVAILABLE
        assert not Booking.objects.filter(seat=seat).exists()

    def test_one_booking_per_seat_is_enforced(self, movie_and_seats):
        """The booking relation prevents two records for a single seat."""
        movie, seat, _ = movie_and_seats
        first_user = User.objects.create_user(
            username="first-booker", password="pass-123"
        )
        second_user = User.objects.create_user(
            username="second-booker", password="pass-123"
        )
        Booking.objects.create(movie=movie, seat=seat, user=first_user)

        with pytest.raises(IntegrityError):
            Booking.objects.create(movie=movie, seat=seat, user=second_user)

    def test_user_can_book_distinct_seats_for_the_same_movie(self, movie_and_seats):
        """There is no per-user booking cap for distinct available seats."""
        movie, first_seat, second_seat = movie_and_seats
        user = User.objects.create_user(username="booker", password="pass-123")

        first_booking = create_booking(user=user, movie=movie, seat=first_seat)
        second_booking = create_booking(user=user, movie=movie, seat=second_seat)

        assert first_booking.pk != second_booking.pk
        assert Booking.objects.filter(user=user, movie=movie).count() == 2
        first_seat.refresh_from_db()
        second_seat.refresh_from_db()
        assert first_seat.status == Seat.STATUS_RESERVED
        assert second_seat.status == Seat.STATUS_RESERVED
