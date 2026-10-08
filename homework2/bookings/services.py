"""Shared domain operations for creating movie seat bookings."""

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Booking, Movie, Seat


class SeatUnavailableError(Exception):
    """Signal that an atomic attempt could not claim an available seat."""


@transaction.atomic
def create_booking(*, user, movie: Movie, seat: Seat) -> Booking:
    """Atomically claim an available seat and persist its booking.

    The conditional update is the concurrency boundary: only one request can
    change a given seat from available to reserved. If creating the Booking
    fails, the transaction rolls the seat status back as well.

    Args:
        user: Authenticated Django user who owns the booking.
        movie: Movie selected for the reservation.
        seat: Seat to claim; it must belong to ``movie``.

    Returns:
        The newly persisted Booking instance.

    Raises:
        ValidationError: If the seat does not belong to the selected movie.
        SeatUnavailableError: If the seat is not currently available.
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
