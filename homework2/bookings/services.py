"""Shared domain operations for creating movie seat bookings."""

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Booking, Movie, Seat


class SeatUnavailableError(Exception):
    """Raised when a seat is no longer available for booking."""


@transaction.atomic
def create_booking(*, user, movie: Movie, seat: Seat) -> Booking:
    """Claim an available seat and create its booking as one transaction.

    The conditional update is the concurrency boundary: only one request can
    change a given seat from available to reserved. If creating the Booking
    fails, the transaction rolls the seat status back as well.
    """
    if not Seat.objects.filter(  # pylint: disable=no-member
        pk=seat.pk, movie=movie
    ).exists():
        raise ValidationError(
            {"seat": "The selected seat does not belong to this movie."}
        )

    claimed_seats = Seat.objects.filter(  # pylint: disable=no-member
        pk=seat.pk,
        movie=movie,
        status=Seat.STATUS_AVAILABLE,
    ).update(status=Seat.STATUS_RESERVED)
    if claimed_seats != 1:
        raise SeatUnavailableError("The seat is unavailable.")

    return Booking.objects.create(  # pylint: disable=no-member
        movie=movie,
        seat=seat,
        user=user,
    )
