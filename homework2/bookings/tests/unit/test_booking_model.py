# pylint: disable=line-too-long
"""Unit tests for the booking persistence model."""

import pytest
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
def test_booking_relations_and_server_set_booking_date():
    """Booking links movie, seat, and user with a server timestamp."""
    movie = Movie.objects.create(
        title="Model test",
        description="A booking model test.",
        release_date="2026-10-08",
        duration=100,
    )
    seat = Seat.objects.create(movie=movie, seat_number="A1")
    user = User.objects.create_user(username="model-booker", password="pass-123")

    booking = Booking.objects.create(movie=movie, seat=seat, user=user)

    assert isinstance(Booking._meta.get_field("movie"), models.ForeignKey)
    assert isinstance(Booking._meta.get_field("seat"), models.OneToOneField)
    assert isinstance(Booking._meta.get_field("user"), models.ForeignKey)
    assert Booking._meta.get_field("booking_date").auto_now_add
    assert booking.booking_date <= timezone.now()
    assert booking.movie == movie
    assert booking.seat == seat
    assert booking.user == user
