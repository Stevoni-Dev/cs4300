"""Unit tests for the user's paginated booking history query."""

# Django adds ORM managers dynamically; Pylint cannot infer these attributes.
# pylint: disable=no-member

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

from bookings.api import BookingViewSet
from bookings.models import Booking, Movie, Seat


User = get_user_model()


def _create_booking_history(user, booking_count):
    """Create bookings with distinct server timestamps for ordering tests."""
    movie = Movie.objects.create(
        title="History test",
        description="A booking history test movie.",
        release_date="2026-10-08",
        duration=100,
    )
    base_time = timezone.now()
    bookings = []
    for index in range(booking_count):
        seat = Seat.objects.create(movie=movie, seat_number=f"H{index:02d}")
        booking = Booking.objects.create(movie=movie, seat=seat, user=user)
        Booking.objects.filter(pk=booking.pk).update(
            booking_date=base_time + timedelta(minutes=index)
        )
        booking.booking_date = base_time + timedelta(minutes=index)
        bookings.append(booking)
    return bookings


def _history_view(page_number="1"):
    """Create an initialized booking viewset request for a selected page."""
    request = RequestFactory().get(
        "/api/bookings/",
        {"page": page_number},
    )
    view = BookingViewSet()
    view.action_map = {"get": "list"}
    view.request = view.initialize_request(request)
    view.args = ()
    view.kwargs = {}
    return view


@pytest.mark.unit
@pytest.mark.django_db
class TestBookingHistory:
    """Check newest-first query order and stable 20-item page boundaries."""

    @pytest.fixture
    def user(self):
        """Create the owner of the history being inspected."""
        return User.objects.create_user(
            username="history-owner",
            password="valid-password-123",
        )

    def test_history_queryset_orders_newest_first(self, user):
        """The history view queryset orders newer booking dates first."""
        bookings = _create_booking_history(user, 3)
        view = _history_view()
        view.request.user = user

        queryset = view.get_queryset()

        assert list(queryset) == list(reversed(bookings))

    def test_history_pagination_has_stable_twenty_item_boundaries(self, user):
        """The newest 20 bookings precede the remaining booking on page two."""
        bookings = _create_booking_history(user, 21)
        newest_first = list(reversed(bookings))

        first_view = _history_view()
        first_view.request.user = user
        first_page = first_view.paginate_queryset(first_view.get_queryset())

        second_view = _history_view("2")
        second_view.request.user = user
        second_page = second_view.paginate_queryset(second_view.get_queryset())

        assert len(first_page) == 20
        assert len(second_page) == 1
        assert list(first_page) == newest_first[:20]
        assert list(second_page) == newest_first[20:]
