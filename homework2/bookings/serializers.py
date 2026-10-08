"""Serializers for public movie and seat reads."""

from __future__ import annotations

from rest_framework import exceptions, serializers

from .models import Booking, Movie, Seat
from .services import create_booking


class NotFoundPrimaryKeyRelatedField(  # pylint: disable=too-few-public-methods
    serializers.PrimaryKeyRelatedField
):
    """Resolve a related model by id and return 404 when it is missing."""

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=data)  # pylint: disable=no-member
        except queryset.model.DoesNotExist as exc:
            raise exceptions.NotFound(
                f"{queryset.model.__name__} not found."
            ) from exc


class MovieSerializer(serializers.ModelSerializer):  # pylint: disable=too-few-public-methods
    """Public representation of a movie."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Fields included in a movie response."""

        model = Movie
        fields = ["id", "title", "description", "release_date", "duration"]


class SeatSerializer(serializers.ModelSerializer):  # pylint: disable=too-few-public-methods
    """Public representation of a seat and its current availability."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Fields included in a seat response."""

        model = Seat
        fields = ["id", "movie", "seat_number", "status"]


class BookingSerializer(serializers.ModelSerializer):  # pylint: disable=too-few-public-methods
    """Accept a movie and seat while keeping owner and date server-controlled."""

    movie_title = serializers.CharField(source="movie.title", read_only=True)
    seat_number = serializers.CharField(source="seat.seat_number", read_only=True)
    movie = NotFoundPrimaryKeyRelatedField(
        queryset=Movie.objects.all(),  # pylint: disable=no-member
        pk_field=serializers.IntegerField(),
    )
    seat = NotFoundPrimaryKeyRelatedField(
        queryset=Seat.objects.all(),  # pylint: disable=no-member
        pk_field=serializers.IntegerField(),
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    booking_date = serializers.DateTimeField(read_only=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Define the API representation and writable booking inputs."""

        model = Booking
        fields = [
            "id",
            "movie",
            "seat",
            "movie_title",
            "seat_number",
            "user",
            "booking_date",
        ]

    def validate(self, attrs):
        """Reject a seat that exists but belongs to a different movie."""
        if attrs["seat"].movie_id != attrs["movie"].pk:
            raise serializers.ValidationError(
                {"seat": "The selected seat does not belong to this movie."}
            )
        return attrs

    def create(self, validated_data):
        """Delegate reservation rules to the shared booking service."""
        return create_booking(
            user=self.context["request"].user,
            movie=validated_data["movie"],
            seat=validated_data["seat"],
        )
