"""Integration tests for registration, sign-in, and booking pages."""

# Django adds ORM managers dynamically; Pylint cannot infer these attributes.
# pylint: disable=no-member

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestRegistrationBookingPages:
    """Exercise the browser workflows that lead to seat reservations."""

    @pytest.fixture
    def movie_inventory(self):
        """Create a movie with two available seats and one other movie."""
        movie = Movie.objects.create(
            title="Inception",
            description="A dream within a dream.",
            release_date="2026-10-07",
            duration=148,
        )
        other_movie = Movie.objects.create(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2026-10-08",
            duration=116,
        )
        first_seat = Seat.objects.create(movie=movie, seat_number="A1")
        second_seat = Seat.objects.create(movie=movie, seat_number="A2")
        return movie, first_seat, second_seat, other_movie

    @pytest.fixture
    def user(self):
        """Create a user who can use the booking page."""
        return User.objects.create_user(
            username="page-booker",
            password="valid-password-123",
        )

    def test_registration_shows_field_errors_and_creates_no_user(self):
        """Invalid registration returns field-specific feedback only."""
        client = Client()

        response = client.post(
            "/register/",
            {
                "username": "new-page-user",
                "password1": "valid-password-123",
                "password2": "different-password-456",
            },
        )

        assert response.status_code == 200
        assert set(response.context["form"].errors) == {"password2"}
        content = response.content.decode()
        assert "errorlist" in content
        assert not User.objects.filter(username="new-page-user").exists()

    def test_registration_accepts_valid_csrf_token_and_creates_account(self):
        """A browser can register with a CSRF token from the form page."""
        client = Client(enforce_csrf_checks=True)
        form_response = client.get("/register/")
        csrf_token = form_response.context["csrf_token"]

        rejected_response = client.post(
            "/register/",
            {
                "username": "csrf-page-user",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
            },
            HTTP_ORIGIN="https://app-mightyraven6850-28.lab.devedu.io",
        )

        assert rejected_response.status_code == 403
        assert not User.objects.filter(username="csrf-page-user").exists()

        response = client.post(
            "/register/",
            {
                "username": "csrf-page-user",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
                "csrfmiddlewaretoken": csrf_token,
            },
            HTTP_ORIGIN="https://app-mightyraven6850-28.lab.devedu.io",
            follow=True,
        )

        assert response.status_code == 200
        assert User.objects.filter(username="csrf-page-user").exists()

    def test_duplicate_registration_shows_username_error(self):
        """The registration page identifies an already-used username."""
        User.objects.create_user(username="taken-user", password="pass-123")
        client = Client()

        response = client.post(
            "/register/",
            {
                "username": "taken-user",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
            },
        )

        assert response.status_code == 200
        assert "username" in response.context["form"].errors
        assert User.objects.filter(username="taken-user").count() == 1

    def test_unknown_and_wrong_password_have_the_same_sign_in_feedback(self):
        """Sign-in failures are generic and do not authenticate the client."""
        User.objects.create_user(username="known-user", password="correct-123")
        client = Client()
        feedback = []

        for credentials in (
            {"username": "unknown-user", "password": "valid-password-123"},
            {"username": "known-user", "password": "wrong-password-456"},
        ):
            response = client.post("/login/", credentials)
            assert response.status_code == 200
            feedback.append(str(response.context["form"].non_field_errors()))
            assert "invalid username or password" in (
                response.content.decode().lower()
            )
            assert "_auth_user_id" not in client.session

        assert feedback[0] == feedback[1]
        assert "invalid username or password" in feedback[0].lower()

    def test_booking_page_confirms_reservation(self, movie_inventory, user):
        """A signed-in user receives confirmation and the seat is reserved."""
        movie, seat, _, _ = movie_inventory
        client = Client()
        client.force_login(user)

        response = client.post(
            "/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
            follow=True,
        )

        assert response.status_code == 200
        content = response.content.decode().lower()
        assert "booking confirmed" in content
        assert 'role="status"' in content
        assert Booking.objects.get(seat=seat).user == user
        seat.refresh_from_db()
        assert seat.status == Seat.STATUS_RESERVED

    def test_booking_page_rejects_authenticated_request_without_csrf(
        self, movie_inventory, user
    ):
        """Unsafe session-authenticated booking submissions require CSRF."""
        movie, seat, _, _ = movie_inventory
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post(
            "/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
        )

        assert response.status_code == 403
        assert not Booking.objects.filter(seat=seat).exists()

    def test_booking_page_explains_when_seat_is_unavailable(
        self, movie_inventory, user
    ):
        """A previously reserved seat gets actionable page feedback."""
        movie, seat, _, _ = movie_inventory
        previous_user = User.objects.create_user(
            username="previous-booker", password="pass-123"
        )
        Booking.objects.create(movie=movie, seat=seat, user=previous_user)
        seat.status = Seat.STATUS_RESERVED
        seat.save(update_fields=["status"])
        client = Client()
        client.force_login(user)

        response = client.post(
            "/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
            follow=True,
        )

        assert response.status_code == 200
        content = response.content.decode().lower()
        assert "unavailable" in content
        assert 'role="alert"' in content
        assert Booking.objects.filter(seat=seat).count() == 1
