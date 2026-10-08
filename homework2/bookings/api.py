"""DRF endpoints for the public catalog and protected booking resources.

Movie and seat reads are public; movie mutations require authentication.
Booking creation and history require authentication and use the configured
session authentication and CSRF behavior.
"""

from __future__ import annotations

from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, permissions, response, status, viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import PageNumberPagination

from .models import Booking, Movie, Seat
from .serializers import BookingSerializer, MovieSerializer, SeatSerializer
from .services import SeatUnavailableError


class SeatConflictError(exceptions.APIException):
    """Return HTTP 409 when an atomic seat claim loses an availability race."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "The seat is unavailable."
    default_code = "seat_unavailable"


class MovieBookingHistoryConflict(exceptions.APIException):
    """Return HTTP 409 when booking history prevents movie deletion."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Movies with booking history cannot be deleted."
    default_code = "booking_history_conflict"


class BookingHistoryPagination(PageNumberPagination):
    """Return booking history in page-number pages of 20 records.

    DRF supplies ``count``, ``next``, ``previous``, and ``results`` in the
    response; clients select the page with the ``page`` query parameter.
    """

    page_size = 20


class MovieViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """Expose public movie reads and authenticated catalog mutations.

    List and detail actions permit anonymous access. Create, replace, partial
    update, and delete actions require an authenticated user.
    """

    queryset = Movie.objects.all().order_by(  # pylint: disable=no-member
        "release_date", "title"
    )
    serializer_class = MovieSerializer

    def get_permissions(self):
        """Select public-read or authenticated-write permissions by action.

        Returns:
            Permission instances configured for the current router action.
        """
        if self.action in {"list", "retrieve"}:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_destroy(self, instance):
        """Delete an unbooked movie or return conflict for protected history.

        Args:
            instance: The movie resolved by DRF for the delete request.

        Raises:
            MovieBookingHistoryConflict: If any booking references the movie.
        """
        try:
            instance.delete()
        except ProtectedError as exc:
            raise MovieBookingHistoryConflict() from exc


class SeatViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Expose public seat detail and movie-scoped availability reads.

    Seat inventory is provisioned separately; this API does not create or
    mutate seats. Collection requests require a valid ``movie`` query value.
    """

    queryset = Seat.objects.select_related("movie").order_by(  # pylint: disable=no-member
        "movie_id", "seat_number"
    )
    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """List seats for one movie or return a validation/not-found response.

        Args:
            request: DRF request with a ``movie`` query parameter.

        Returns:
            A JSON array of seats belonging to the requested movie.

        Raises:
            ValidationError: If ``movie`` is missing or not an integer.
            Http404: If the movie ID does not exist.
        """
        movie_id = request.query_params.get("movie")
        if movie_id is None:
            raise exceptions.ValidationError(
                {"movie": "This query parameter is required."}
            )

        try:
            movie_id = int(movie_id)
        except (TypeError, ValueError) as exc:
            raise exceptions.ValidationError(
                {"movie": "This query parameter must be an integer."}
            ) from exc

        movie = get_object_or_404(Movie, pk=movie_id)
        queryset = self.filter_queryset(self.get_queryset()).filter(
            movie=movie
        )
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)


class BookingViewSet(
    ListModelMixin,
    CreateModelMixin,
    viewsets.GenericViewSet,
):  # pylint: disable=too-many-ancestors
    """List the authenticated user's history and create their bookings.

    GET results are user-scoped, newest first, and paginated. POST accepts a
    movie and seat; ownership and booking time are assigned server-side.
    """

    queryset = Booking.objects.select_related(  # pylint: disable=no-member
        "movie", "seat", "user"
    )
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = BookingHistoryPagination

    def get_queryset(self):
        """Return the authenticated user's bookings, newest first.

        Returns:
            Booking rows for ``request.user``, with related
            display data loaded.
        """
        return super().get_queryset().filter(  # pylint: disable=no-member
            user=self.request.user
        ).select_related(
            "movie", "seat", "user"
        ).order_by("-booking_date", "-pk")

    def perform_create(self, serializer):
        """Persist a booking and translate unavailable seats to HTTP 409.

        Args:
            serializer: Validated booking serializer using the request user.
        """
        try:
            serializer.save()
        except SeatUnavailableError as exc:
            raise SeatConflictError(detail=str(exc)) from exc
