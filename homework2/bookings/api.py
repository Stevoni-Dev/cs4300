"""Public read-only DRF viewsets for movies and seats."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import exceptions, permissions, response, status, viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import PageNumberPagination

from .models import Booking, Movie, Seat
from .serializers import BookingSerializer, MovieSerializer, SeatSerializer
from .services import SeatUnavailableError


class SeatConflictError(exceptions.APIException):
    """Represent an unavailable seat as the contract's conflict response."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "The seat is unavailable."
    default_code = "seat_unavailable"


class BookingHistoryPagination(PageNumberPagination):
    """Paginate each user's booking history in pages of twenty records."""

    page_size = 20


class MovieViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Public movie list and detail endpoints."""

    queryset = Movie.objects.all().order_by(  # pylint: disable=no-member
        "release_date", "title"
    )
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]


class SeatViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Public movie-scoped seat list and detail endpoints."""

    queryset = Seat.objects.select_related("movie").order_by(  # pylint: disable=no-member
        "movie_id", "seat_number"
    )
    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
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
    """Create one booking for the authenticated user."""

    queryset = Booking.objects.select_related(  # pylint: disable=no-member
        "movie", "seat", "user"
    )
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = BookingHistoryPagination

    def get_queryset(self):
        """Return only the request user's bookings, newest first."""
        return super().get_queryset().filter(  # pylint: disable=no-member
            user=self.request.user
        ).select_related(
            "movie", "seat", "user"
        ).order_by("-booking_date", "-pk")

    def perform_create(self, serializer):
        """Translate a lost seat claim into the documented 409 response."""
        try:
            serializer.save()
        except SeatUnavailableError as exc:
            raise SeatConflictError(detail=str(exc)) from exc
