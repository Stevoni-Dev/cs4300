"""Server-rendered movie, account, reservation, and history page handlers."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, SeatBookingForm, SignInForm
from .models import Booking, Movie
from .services import SeatUnavailableError, create_booking


def movie_list_view(request):
    """Render the public movie catalog, ordered for browsing.

    Args:
        request: Incoming Django request.

    Returns:
        The movie listing response with available-seat counts.
    """
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
    """Render one movie and its seat status labels.

    Args:
        request: Incoming Django request.
        pk: Primary key of the movie to display.

    Returns:
        The movie detail response, or HTTP 404 for an unknown movie.
    """
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
    """Render registration errors or save a valid new account.

    Args:
        request: GET renders a blank form; POST validates the submitted data.

    Returns:
        The registration page, or a redirect to sign-in after successful save.
    """
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
    """Authenticate credentials and establish a Django session on success.

    Args:
        request: GET renders the form; POST validates credentials.

    Returns:
        The sign-in page with generic errors or a redirect to the movie list.
    """
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
    """End the current session on a CSRF-protected POST.

    Args:
        request: POST request from the current browser session.

    Returns:
        A redirect to the public movie list.
    """
    logout(request)
    return redirect("movie-list")


@login_required(login_url="login")
@require_POST
def booking_create_view(request):
    """Book one seat for a signed-in user through the shared domain service.

    Args:
        request: POST with movie and seat IDs; login and CSRF are required.

    Returns:
        A redirect to the movie detail page with success/conflict messaging,
        or a 400 response containing invalid form fields.
    """
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


@login_required(login_url="login")
def booking_history_view(request):
    """Render the signed-in user's history newest first, 20 records per page.

    Args:
        request: Authenticated request with an optional ``page`` query value.

    Returns:
        The private booking history page with an empty state when appropriate.
    """
    booking_list = Booking.objects.filter(  # pylint: disable=no-member
        user=request.user
    ).select_related(
        "movie", "seat"
    ).order_by("-booking_date", "-pk")
    paginator = Paginator(booking_list, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "bookings/booking_history.html",
        {"page": page},
    )
