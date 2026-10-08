"""Page integration tests for private booking history."""

# Django adds ORM managers dynamically; Pylint cannot infer these attributes.
# pylint: disable=no-member,duplicate-code

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestBookingHistoryPages:
    """Exercise the signed-in booking history page and its pagination."""

    @pytest.fixture
    def history(self):
        """Create 21 owner bookings and a newer booking owned by someone else."""
        owner = User.objects.create_user(
            username="history-page-owner",
            password="valid-password-123",
        )
        other_user = User.objects.create_user(
            username="history-page-other",
            password="valid-password-123",
        )
        movie = Movie.objects.create(
            title="History Page",
            description="A movie used by booking history page tests.",
            release_date="2026-10-08",
            duration=100,
        )
        base_time = timezone.now()
        owner_bookings = []
        for index in range(21):
            seat = Seat.objects.create(movie=movie, seat_number=f"P{index:02d}")
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

    def test_history_page_is_private_newest_first_and_paginated(self, history):
        """The page shows only 20 newest owner bookings and a next-page link."""
        owner, owner_bookings, private_booking = history
        client = Client()
        client.force_login(owner)

        first_response = client.get("/bookings/history/")

        assert first_response.status_code == 200
        first_page = first_response.content.decode()
        assert "History Page" in first_page
        assert "PRIVATE" not in first_page
        assert "P20" in first_page
        assert "P01" in first_page
        assert "P00" not in first_page
        assert "page=2" in first_page
        assert first_page.index("P20") < first_page.index("P01")
        assert private_booking.seat.seat_number not in first_page

        second_response = client.get("/bookings/history/?page=2")
        assert second_response.status_code == 200
        second_page = second_response.content.decode()
        assert "P00" in second_page
        assert "P20" not in second_page
        assert "page=1" in second_page
        assert len(owner_bookings) == 21

    def test_empty_history_page_has_helpful_empty_state(self):
        """A signed-in user without bookings sees an informative empty state."""
        user = User.objects.create_user(
            username="empty-history-page",
            password="valid-password-123",
        )
        client = Client()
        client.force_login(user)

        response = client.get("/bookings/history/")

        assert response.status_code == 200
        page = response.content.decode().lower()
        assert "no bookings" in page or "no booking history" in page
