"""Public movie browsing views for visitors."""

from __future__ import annotations

from django.shortcuts import get_object_or_404, render

from .models import Movie


def movie_list_view(request):
    """Display the list of available movies to visitors."""
    movies = Movie.objects.order_by(
        "release_date", "title"
    )
    for movie in movies:
        movie.available_seats_count = movie.seats.filter(
            status="available"
        ).count()
    return render(
        request,
        "bookings/movie_list.html",
        {"movies": movies},
    )


def movie_detail_view(request, pk):
    """Display a movie and label its reserved and available seats."""
    movie = get_object_or_404(Movie, pk=pk)
    seats = movie.seats.order_by("seat_number")
    return render(
        request,
        "bookings/movie_detail.html",
        {
            "movie": movie,
            "seats": seats,
        },
    )
