"""Serializers for public movie and seat reads."""

from __future__ import annotations

from rest_framework import serializers

from .models import Movie, Seat


class MovieSerializer(serializers.ModelSerializer):
    """Public representation of a movie."""

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date", "duration"]


class SeatSerializer(serializers.ModelSerializer):
    """Public representation of a seat and its current availability."""

    class Meta:
        model = Seat
        fields = ["id", "movie", "seat_number", "status"]
