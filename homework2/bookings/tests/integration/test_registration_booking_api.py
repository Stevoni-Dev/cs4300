"""Integration tests for account access and booking API behavior."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.db import connection, connections
from rest_framework.test import APIClient

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestRegistrationBookingApi:
    """Exercise authentication, validation, and persisted API bookings."""

    @pytest.fixture
    def movie_inventory(self):
        """Create two movies and two available seats for the first movie."""
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
        foreign_seat = Seat.objects.create(movie=other_movie, seat_number="B1")
        return movie, first_seat, second_seat, foreign_seat

    @pytest.fixture
    def user(self):
        """Create an account used by authenticated booking requests."""
        return User.objects.create_user(
            username="api-booker",
            password="valid-password-123",
        )

    def test_registration_failure_reports_fields_without_creating_user(self):
        """Invalid registration identifies fields and persists no account."""
        client = APIClient()

        response = client.post(
            "/register/",
            {
                "username": "",
                "password1": "valid-password-123",
                "password2": "different-password-456",
            },
        )

        assert response.status_code == 200
        assert b"username" in response.content.lower()
        assert not User.objects.filter(username="").exists()

    def test_duplicate_registration_does_not_create_an_account(self):
        """Registration rejects a duplicate username and keeps one account."""
        User.objects.create_user(username="taken-user", password="pass-123")
        client = APIClient()

        response = client.post(
            "/register/",
            {
                "username": "taken-user",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
            },
        )

        assert response.status_code == 200
        assert b"username" in response.content.lower()
        assert User.objects.filter(username="taken-user").count() == 1

    @pytest.mark.parametrize(
        "credentials",
        [
            {"username": "unknown-user", "password": "valid-password-123"},
            {"username": "known-user", "password": "wrong-password-456"},
        ],
    )
    def test_failed_sign_in_uses_generic_message_without_session(
        self, credentials
    ):
        """Unknown accounts and wrong passwords have the same failure text."""
        User.objects.create_user(username="known-user", password="correct-123")
        client = APIClient()

        response = client.post("/login/", credentials)

        assert response.status_code == 200
        assert b"invalid username or password" in response.content.lower()
        assert "_auth_user_id" not in client.session

    def test_booking_rejects_anonymous_request_with_native_drf_response(
        self, movie_inventory
    ):
        """Anonymous booking uses configured DRF auth and stores nothing."""
        movie, seat, _, _ = movie_inventory
        client = APIClient()

        response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
            format="json",
        )

        assert response.status_code == 403
        assert "WWW-Authenticate" not in response
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }
        assert not Booking.objects.filter(seat=seat).exists()

    def test_session_authenticated_booking_rejects_invalid_csrf(
        self, movie_inventory, user
    ):
        """Session-authenticated API mutations require a valid CSRF token."""
        movie, seat, _, _ = movie_inventory
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
            format="json",
        )

        assert response.status_code == 403
        assert response.json()["detail"].startswith("CSRF Failed:")
        assert not Booking.objects.filter(seat=seat).exists()

    def test_booking_creates_record_for_authenticated_user(
        self, movie_inventory, user
    ):
        """Booking creation stores the session user and ignores fields."""
        movie, seat, _, _ = movie_inventory
        client = APIClient()
        client.force_login(user)

        forged_user = User.objects.create_user(
            username="forged-user", password="pass-123"
        )
        response = client.post(
            "/api/bookings/",
            {
                "movie": movie.pk,
                "seat": seat.pk,
                "user": forged_user.pk,
                "booking_date": "2000-01-01T00:00:00Z",
            },
            format="json",
        )

        assert response.status_code == 201
        booking = Booking.objects.get(seat=seat)
        assert booking.user == user
        assert booking.movie == movie
        assert booking.booking_date.year != 2000
        seat.refresh_from_db()
        assert seat.status == Seat.STATUS_RESERVED

    def test_booking_returns_not_found_for_unknown_movie_or_seat(
        self, movie_inventory, user
    ):
        """Unknown movie and seat identifiers return 404 without booking."""
        movie, seat, _, _ = movie_inventory
        client = APIClient()
        client.force_login(user)

        unknown_movie = client.post(
            "/api/bookings/",
            {"movie": 999999, "seat": seat.pk},
            format="json",
        )
        unknown_seat = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": 999999},
            format="json",
        )

        assert unknown_movie.status_code == 404
        assert unknown_seat.status_code == 404
        assert Booking.objects.count() == 0

    def test_booking_rejects_seat_from_a_different_movie(
        self, movie_inventory, user
    ):
        """An existing seat outside the selected movie is a 400 error."""
        movie, _, _, foreign_seat = movie_inventory
        client = APIClient()
        client.force_login(user)

        response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": foreign_seat.pk},
            format="json",
        )

        assert response.status_code == 400
        assert Booking.objects.count() == 0

    def test_reserved_seat_returns_conflict_and_unavailable_message(
        self, movie_inventory, user
    ):
        """A seat can be claimed once and later requests explain the issue."""
        movie, seat, _, _ = movie_inventory
        first_user = User.objects.create_user(
            username="first-booker", password="pass-123"
        )
        Booking.objects.create(movie=movie, seat=seat, user=first_user)
        seat.status = Seat.STATUS_RESERVED
        seat.save(update_fields=["status"])
        client = APIClient()
        client.force_login(user)

        response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
            format="json",
        )

        assert response.status_code == 409
        assert "unavailable" in str(response.json()).lower()
        assert Booking.objects.filter(seat=seat).count() == 1

    def test_user_can_create_multiple_distinct_bookings(
        self, movie_inventory, user
    ):
        """One user may reserve multiple seats for the same movie."""
        movie, first_seat, second_seat, _ = movie_inventory
        client = APIClient()
        client.force_login(user)

        first_response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": first_seat.pk},
            format="json",
        )
        second_response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": second_seat.pk},
            format="json",
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201
        assert Booking.objects.filter(user=user, movie=movie).count() == 2


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="The concurrency contract must be validated on PostgreSQL.",
)
def test_competing_requests_create_one_booking_and_one_conflict():
    """Synchronized independent DB connections cannot double-book a seat."""
    movie = Movie.objects.create(
        title="Concurrency",
        description="A synchronized booking test.",
        release_date="2026-10-09",
        duration=100,
    )
    seat = Seat.objects.create(movie=movie, seat_number="C1")
    users = [
        User.objects.create_user(
            username=f"concurrent-{user_index}", password="pass-123"
        )
        for user_index in range(2)
    ]
    start = Barrier(2)

    def submit_booking(user):
        """Submit after both workers have independent DB connections."""
        connections.close_all()
        client = APIClient()
        client.force_authenticate(user=user)
        start.wait(timeout=10)
        response = client.post(
            "/api/bookings/",
            {"movie": movie.pk, "seat": seat.pk},
            format="json",
        )
        connections.close_all()
        return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(submit_booking, users))

    statuses = sorted(status for status, _ in responses)
    conflict_body = next(body for status, body in responses if status == 409)
    assert statuses == [201, 409]
    assert "unavailable" in str(conflict_body).lower()
    assert Booking.objects.filter(seat=seat).count() == 1
