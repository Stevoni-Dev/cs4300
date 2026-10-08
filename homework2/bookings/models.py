"""Domain models for the movie theater booking application."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Movie(models.Model):
    """A movie listed for booking in the theater."""

    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    release_date = models.DateField(blank=False, null=False)
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], blank=False, null=False
    )

    def clean(self):
        """Reject whitespace-only text fields during model validation.

        ``full_clean()`` reports errors under ``title`` or ``description``;
        callers should validate before saving when constructing models outside
        serializer or form validation.
        """
        super().clean()
        if (
            self.title is not None
            and not self.title.strip()  # pylint: disable=no-member
        ):
            raise ValidationError({"title": "This field cannot be blank."})
        if self.description is not None and not self.description.strip():  # pylint: disable=no-member
            raise ValidationError(
                {"description": "This field cannot be blank."}
            )

    def __str__(self) -> str:
        """Return the movie's display title."""
        return str(self.title)


class Seat(models.Model):  # pylint: disable=too-few-public-methods
    """A numbered seat that belongs to a movie inventory."""

    STATUS_AVAILABLE = "available"
    STATUS_RESERVED = "reserved"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
    ]

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="seats",
    )
    seat_number = models.CharField(max_length=10, blank=False, null=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
        blank=False,
        null=False,
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Uniqueness rules for a movie's seat inventory."""

        constraints = [
            models.UniqueConstraint(
                fields=["movie", "seat_number"],
                name="unique_movie_seat_number",
            )
        ]

    def clean(self):
        """Reject a blank seat label during model validation.

        Database uniqueness for a seat label within one movie is enforced by
        the ``unique_movie_seat_number`` constraint.
        """
        super().clean()
        if (
            not self.seat_number
            or not self.seat_number.strip()  # pylint: disable=no-member
        ):
            raise ValidationError(
                {"seat_number": "This field cannot be blank."}
            )

    def __str__(self) -> str:
        """Return a movie-scoped seat identifier for logs and admin lists."""
        return f"{self.movie_id}:{self.seat_number}"  # pylint: disable=no-member


class Booking(models.Model):
    """A confirmed reservation connecting a user, movie, and unique seat.

    ``booking_date`` is assigned by Django at insertion. The protected movie
    and seat relations preserve records referenced by booking history.
    """

    movie = models.ForeignKey(
        Movie,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    seat = models.OneToOneField(
        Seat,
        on_delete=models.PROTECT,
        related_name="booking",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return a concise movie, seat, and owner description."""
        return (  # pylint: disable=no-member
            f"{self.movie.title} - {self.seat.seat_number} ({self.user})"
        )
