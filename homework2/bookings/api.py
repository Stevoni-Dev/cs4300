"""Shared DRF API helpers and public read-only viewsets for the bookings app."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import exceptions, permissions, response, serializers, viewsets
from rest_framework.views import exception_handler as drf_exception_handler

from .models import Movie, Seat
from .serializers import MovieSerializer, SeatSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """Public movie list and detail endpoints."""

    queryset = Movie.objects.all().order_by("release_date", "title")
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """Public movie-scoped seat list and detail endpoints."""

    queryset = Seat.objects.select_related("movie").order_by("movie_id", "seat_number")
    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        movie_id = request.query_params.get("movie")
        if movie_id is None:
            raise exceptions.ValidationError({"movie": "This query parameter is required."})

        try:
            movie_id = int(movie_id)
        except (TypeError, ValueError) as exc:
            raise exceptions.ValidationError({"movie": "This query parameter must be an integer."}) from exc

        movie = get_object_or_404(Movie, pk=movie_id)
        queryset = self.filter_queryset(self.get_queryset()).filter(movie=movie)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)


def custom_exception_handler(exc, context):
    """Normalize DRF auth failures to the project contract.

    Anonymous requests to protected endpoints must be 401 with the expected
    JSON error shape, while authenticated forbidden requests (including invalid
    CSRF) remain 403.
    """
    response_obj = drf_exception_handler(exc, context)
    if response_obj is None:
        return None

    request = context.get("request")
    user = getattr(request, "user", None) if request is not None else None
    is_authenticated = bool(
        user is not None and getattr(user, "is_authenticated", False)
    )

    if isinstance(
        exc,
        (exceptions.NotAuthenticated, exceptions.AuthenticationFailed),
    ):
        detail = str(getattr(exc, "detail", "Authentication credentials were not provided."))
        if "CSRF Failed:" in detail:
            response_obj.status_code = 403
            response_obj.data = {"detail": detail}
            return response_obj
        response_obj.status_code = 401
        response_obj.data = {
            "detail": "Authentication credentials were not provided."
        }
        return response_obj

    if isinstance(exc, exceptions.PermissionDenied):
        detail = str(getattr(exc, "detail", ""))
        if "CSRF Failed:" in detail:
            response_obj.status_code = 403
            response_obj.data = {"detail": detail}
            return response_obj
        if not is_authenticated:
            response_obj.status_code = 401
            response_obj.data = {
                "detail": "Authentication credentials were not provided."
            }
            return response_obj

    if isinstance(response_obj.data, dict):
        detail = str(response_obj.data.get("detail", ""))
        if "CSRF Failed:" in detail:
            response_obj.status_code = 403
            response_obj.data = {"detail": detail}
            return response_obj

    return response_obj
