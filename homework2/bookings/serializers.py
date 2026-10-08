"""Serialize public catalog reads, inventory writes, and booking requests.

Movie fields are validated on create and update. Seat writes are validated on
create and update: each seat must have a nonblank trimmed ``seat_number`` for
its movie, duplicate labels within the same movie are rejected, the movie is
required on create and ignored on update, and ``status`` is always server-
controlled as ``available``. Booking ownership and time remain server-
controlled; unknown movie or seat identifiers return not-found responses
before the shared booking service claims inventory.
"""

from __future__ import annotations

from rest_framework import exceptions, serializers

from .models import Booking, Movie, Seat
from .services import create_booking


class NotFoundPrimaryKeyRelatedField(  # pylint: disable=too-few-public-methods
    serializers.PrimaryKeyRelatedField
):
    """Resolve a related model identifier with API not-found semantics.

    ``queryset`` supplies the model lookup. Invalid primary-key syntax remains
    a serializer validation error; a well-formed but absent identifier raises
    DRF's ``NotFound`` exception and produces HTTP 404.
    """

    def to_internal_value(self, data):
        """Convert a submitted primary key to an instance or API exception."""
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
    """Validate movie writes and serialize public catalog fields.

    Create and update operations require a nonblank title of at most 200
    characters, a nonblank description, an ISO date, and positive integer
    duration. Read responses include the same fields plus the database ID.
    """

    title = serializers.CharField(
        max_length=200,
        allow_blank=False,
        trim_whitespace=True,
    )
    description = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )
    release_date = serializers.DateField()
    duration = serializers.IntegerField(min_value=1)

    class Meta:  # pylint: disable=too-few-public-methods
        """Fields included in a movie response."""

        model = Movie
        fields = ["id", "title", "description", "release_date", "duration"]


class SeatNumberField(serializers.CharField):
    """Reject non-string seat labels before DRF coerces them to text."""

    def to_internal_value(self, data):
        """Require a real string label and keep whitespace trimming intact."""
        if not isinstance(data, str):
            raise serializers.ValidationError("This field must be a string.")
        return super().to_internal_value(data)


class SeatSerializer(
    serializers.ModelSerializer
):  # pylint: disable=too-few-public-methods
    """Validate seat inventory writes and serialize movie-scoped seat data.

    Create requests require a valid movie and a nonblank seat number; update
    requests may rename the seat but keep it within the same movie and ignore
    any client-provided ``status``/``movie`` values. Responses always include
    the movie ID, label, and the server-controlled availability state.
    """

    movie = NotFoundPrimaryKeyRelatedField(
        queryset=Movie.objects.all(),  # pylint: disable=no-member
        pk_field=serializers.IntegerField(),
    )
    seat_number = SeatNumberField(
        max_length=10,
        allow_blank=False,
        trim_whitespace=True,
    )
    status = serializers.ReadOnlyField()

    class Meta:  # pylint: disable=too-few-public-methods
        """Fields included in a seat response."""

        model = Seat
        fields = ["id", "movie", "seat_number", "status"]
        validators = []

    def validate(self, attrs):
        """Reject duplicate seat labels within the same movie."""
        if self.instance is not None:
            movie = attrs.get("movie", self.instance.movie)
            seat_number = attrs.get("seat_number", self.instance.seat_number)
        else:
            movie = attrs.get("movie")
            seat_number = attrs.get("seat_number")

        if movie is not None and seat_number is not None:
            queryset = Seat.objects.filter(
                movie=movie,
                seat_number=seat_number,
            )
            if self.instance is not None:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "seat_number": (
                            "This seat number is already used "
                            "for this movie."
                        )
                    }
                )
        return attrs

    def create(self, validated_data):
        """Persist new seats as available inventory regardless of input."""
        validated_data["status"] = Seat.STATUS_AVAILABLE
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ignore client-supplied movie/status fields on updates."""
        validated_data.pop("movie", None)
        validated_data.pop("status", None)
        return super().update(instance, validated_data)


class BookingSerializer(
    serializers.ModelSerializer
):  # pylint: disable=too-few-public-methods
    """Serialize bookings while keeping owner and date server-controlled.

    Create requests accept movie and seat primary keys. The authenticated
    request user and server timestamp are read-only; responses also include
    movie title and seat label for history display.
    """

    movie_title = serializers.CharField(
        source="movie.title",
        read_only=True,
    )
    seat_number = serializers.CharField(
        source="seat.seat_number",
        read_only=True,
    )
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
        """Reject existing seats that do not belong to the selected movie.

        Args:
            attrs: Validated movie and seat model instances.

        Returns:
            The validated fields when their movie/seat relationship is valid.

        Raises:
            serializers.ValidationError: If the seat belongs to another movie.
        """
        if attrs["seat"].movie_id != attrs["movie"].pk:
            raise serializers.ValidationError(
                {"seat": "The selected seat does not belong to this movie."}
            )
        return attrs

    def create(self, validated_data):
        """Create a booking through the shared atomic reservation service.

        Args:
            validated_data: Validated movie and seat instances.

        Returns:
            The persisted Booking owned by the authenticated request user.

        Raises:
            ValidationError: If the seat/movie relationship is invalid.
            SeatUnavailableError: If the seat can no longer be claimed.
        """
        return create_booking(
            user=self.context["request"].user,
            movie=validated_data["movie"],
            seat=validated_data["seat"],
        )
