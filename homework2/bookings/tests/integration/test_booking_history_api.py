# pylint: disable=line-too-long
"""Integration tests for private, paginated booking history API results."""

# Django adds ORM managers dynamically; Pylint cannot infer these attributes.
# pylint: disable=no-member,duplicate-code

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestBookingHistoryApi:
    """Exercise booking history authentication, scoping, and pagination."""

    @pytest.fixture
    def history(self):
        """Create 21 bookings for one user and one private booking for another."""
        owner = User.objects.create_user(
            username="history-owner-api",
            password="valid-password-123",
        )
        other_user = User.objects.create_user(
            username="other-history-api",
            password="valid-password-123",
        )
        movie = Movie.objects.create(
            title="History API",
            description="A movie used by booking history API tests.",
            release_date="2026-10-08",
            duration=100,
        )
        base_time = timezone.now()
        owner_bookings = []
        for index in range(21):
            seat = Seat.objects.create(movie=movie, seat_number=f"A{index:02d}")
            booking = Booking.objects.create(
                movie=movie,
                seat=seat,
                user=owner,
            )
            Booking.objects.filter(pk=booking.pk).update(
                booking_date=base_time + timedelta(minutes=index)
            )
            owner_bookings.append(booking)

        private_seat = Seat.objects.create(movie=movie, seat_number="PRIVATE")
        private_booking = Booking.objects.create(
            movie=movie,
            seat=private_seat,
            user=other_user,
        )
        Booking.objects.filter(pk=private_booking.pk).update(
            booking_date=base_time + timedelta(days=1)
        )
        return owner, owner_bookings, private_booking

    def test_anonymous_history_uses_native_drf_permission_response(self):
        """Anonymous history requests are rejected before data is returned."""
        response = APIClient().get("/api/bookings/")

        assert response.status_code == 403
        assert "WWW-Authenticate" not in response
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_history_is_user_scoped_newest_first_and_paged_by_twenty(
        self, history
    ):
        """History returns only owner records with stable newest-first pages."""
        owner, owner_bookings, private_booking = history
        client = APIClient()
        client.force_login(owner)

        first_response = client.get("/api/bookings/")
        assert first_response.status_code == 200
        first_page = first_response.json()
        expected_newest = list(reversed(owner_bookings))

        assert set(first_page) == {"count", "next", "previous", "results"}
        assert first_page["count"] == 21
        assert first_page["previous"] is None
        assert first_page["next"] is not None
        assert len(first_page["results"]) == 20
        assert [item["id"] for item in first_page["results"]] == [
            booking.pk for booking in expected_newest[:20]
        ]
        assert all("movie_title" in item for item in first_page["results"])
        assert all("seat_number" in item for item in first_page["results"])
        assert private_booking.seat_id not in {
            item["seat"] for item in first_page["results"]
        }

        second_response = client.get("/api/bookings/?page=2")
        assert second_response.status_code == 200
        second_page = second_response.json()
        assert second_page["count"] == 21
        assert second_page["previous"] is not None
        assert second_page["next"] is None
        assert [item["id"] for item in second_page["results"]] == [
            expected_newest[20].pk
        ]

    def test_empty_history_has_zero_count_and_empty_results(self):
        """A signed-in user with no bookings gets an explicit empty page."""
        user = User.objects.create_user(
            username="empty-history-api",
            password="valid-password-123",
        )
        client = APIClient()
        client.force_login(user)

        response = client.get("/api/bookings/")

        assert response.status_code == 200
        assert response.json()["count"] == 0
        assert response.json()["results"] == []
