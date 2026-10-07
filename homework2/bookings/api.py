"""Shared DRF API helpers and public read-only viewsets for the bookings app."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import exceptions, permissions, response, viewsets

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
