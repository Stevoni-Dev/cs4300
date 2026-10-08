"""Public movie browsing views for visitors."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegistrationForm, SeatBookingForm, SignInForm
from .models import Movie
from .services import SeatUnavailableError, create_booking


def movie_list_view(request):
    """Display the list of available movies to visitors."""
    movies = Movie.objects.order_by(  # pylint: disable=no-member
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


def registration_view(request):
    """Register a user after validating the submitted account details."""
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(
        request,
        "bookings/registration.html",
        {"form": form},
    )


def login_view(request):
    """Sign a user in only after valid credentials are confirmed."""
    form = SignInForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("movie-list")
    return render(
        request,
        "bookings/login.html",
        {"form": form},
    )


@require_POST
def logout_view(request):
    """End the current authenticated session through a CSRF-protected POST."""
    logout(request)
    return redirect("movie-list")


@login_required(login_url="login")
@require_POST
def booking_create_view(request):
    """Reserve one movie seat through the shared booking service."""
    form = SeatBookingForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "bookings/seat_booking.html",
            {"form": form},
            status=400,
        )

    movie = form.cleaned_data["movie"]
    seat = form.cleaned_data["seat"]
    try:
        create_booking(user=request.user, movie=movie, seat=seat)
    except SeatUnavailableError:
        messages.error(request, f"Seat {seat.seat_number} is unavailable.")
    else:
        messages.success(
            request,
            f"Booking confirmed for seat {seat.seat_number}.",
        )
    return redirect("movie-detail", pk=movie.pk)
