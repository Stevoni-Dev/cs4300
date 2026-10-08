"""Smoke-step definitions for the Behave-Django test harness."""

from __future__ import annotations

import re
from datetime import timedelta

from behave import given, then, when
from django.apps import apps
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@given("the Django app is ready")  # pylint: disable=not-callable
def step_django_app_ready(_context):
    """Assert the app is configured to serve the Django settings module."""
    assert settings.configured is True


@then("the settings module is configured")  # pylint: disable=not-callable
def step_settings_module_configured(_context):
    """Verify the Django settings module was loaded and usable."""
    assert settings.configured is True
    assert "default" in settings.DATABASES
    assert "ENGINE" in settings.DATABASES["default"]


@given('movie "{title}" has available seats "{first}" and "{second}"')  # pylint: disable=not-callable
def step_movie_has_available_seats(context, title, first, second):
    """Create a movie and the two available seats used by a scenario."""
    context.movie = Movie.objects.create(  # pylint: disable=no-member
        title=title,
        description="A feature-test movie.",
        release_date="2026-10-08",
        duration=120,
    )
    context.seats = {
        seat_number: Seat.objects.create(  # pylint: disable=no-member
            movie=context.movie,
            seat_number=seat_number,
        )
        for seat_number in (first, second)
    }


@given("the visitor opens the registration page")  # pylint: disable=not-callable
def step_visitor_opens_registration_page(context):
    """Open registration and retain the browser session for later steps."""
    context.browser_client = Client()
    context.response = context.browser_client.get("/register/")
    assert context.response.status_code == 200


@given("the visitor opens registration with CSRF checks enabled")  # pylint: disable=not-callable
def step_visitor_opens_registration_with_csrf(context):
    """Load the registration form with browser-like CSRF enforcement."""
    context.browser_client = Client(enforce_csrf_checks=True)
    context.response = context.browser_client.get("/register/")
    assert context.response.status_code == 200
    token_match = re.search(
        r'name="csrfmiddlewaretoken"\s+value="([^"]+)"',
        context.response.content.decode(),
    )
    assert token_match is not None
    context.csrf_token = token_match.group(1)


@when(  # pylint: disable=not-callable
    'the visitor registers with username "{username}" '
    'and password "{password}"'
)
def step_visitor_registers(context, username, password):
    """Submit the registration form through its HTML route."""
    context.response = context.browser_client.post(
        "/register/",
        {
            "username": username,
            "password1": password,
            "password2": password,
        },
        follow=True,
    )


@when(  # pylint: disable=not-callable
    'the visitor submits valid CSRF-protected registration data '
    'for "{username}"'
)
def step_visitor_submits_csrf_registration(context, username):
    """Submit valid registration details with the rendered form token."""
    password = "valid-password-123"
    registration_data = {
        "username": username,
        "password1": password,
        "password2": password,
    }
    rejected_response = context.browser_client.post(
        "/register/",
        registration_data,
        HTTP_ORIGIN="https://app-mightyraven6850-28.lab.devedu.io",
    )
    assert rejected_response.status_code == 403
    assert not User.objects.filter(username=username).exists()

    context.response = context.browser_client.post(
        "/register/",
        {**registration_data, "csrfmiddlewaretoken": context.csrf_token},
        HTTP_ORIGIN="https://app-mightyraven6850-28.lab.devedu.io",
        follow=True,
    )
    assert context.response.status_code == 200


@then('account "{username}" exists')  # pylint: disable=not-callable
def step_account_exists(_context, username):
    """Verify registration created the requested account."""
    assert User.objects.filter(username=username).exists()


@when(  # pylint: disable=not-callable
    'the visitor signs in with username "{username}" '
    'and password "{password}"'
)
def step_visitor_signs_in(context, username, password):
    """Submit the sign-in form using the registration browser session."""
    context.response = context.browser_client.post(
        "/login/",
        {"username": username, "password": password},
        follow=True,
    )


@then("the visitor is signed in")  # pylint: disable=not-callable
def step_visitor_is_signed_in(context):
    """Check that sign-in established Django's authenticated session."""
    assert "_auth_user_id" in context.browser_client.session


@when('the visitor browses movie "{title}"')  # pylint: disable=not-callable
def step_visitor_browses_movie(context, title):
    """Open the movie detail page in the signed-in browser session."""
    context.response = context.browser_client.get(
        f"/movies/{context.movie.pk}/"
    )
    assert context.movie.title == title


@then('the page shows available seats "{first}" and "{second}"')  # pylint: disable=not-callable
def step_page_shows_available_seats(context, first, second):
    """Verify the detail page displays both available seat identifiers."""
    page = context.response.content.decode().lower()
    assert first.lower() in page
    assert second.lower() in page
    assert "available" in page


@when('the signed-in visitor books seat "{seat_number}"')  # pylint: disable=not-callable
def step_signed_in_visitor_books_seat(context, seat_number):
    """Submit one seat booking through the HTML booking route."""
    seat = context.seats[seat_number]
    context.response = context.browser_client.post(
        "/bookings/",
        {"movie": context.movie.pk, "seat": seat.pk},
        follow=True,
    )


@then('the booking is confirmed for seat "{seat_number}"')  # pylint: disable=not-callable
def step_booking_is_confirmed(context, seat_number):
    """Verify the page confirms a booking and the seat is reserved."""
    page = context.response.content.decode().lower()
    assert "booking confirmed" in page
    assert seat_number.lower() in page
    seat = context.seats[seat_number]
    seat.refresh_from_db()
    assert seat.status == Seat.STATUS_RESERVED


@given('accounts "{first}" and "{second}" exist')  # pylint: disable=not-callable
def step_two_accounts_exist(context, first, second):
    """Create two distinct accounts and their browser clients."""
    context.browser_clients = {
        username: _create_signed_in_client(username)
        for username in (first, second)
    }


@given('account "{username}" exists and is signed in')  # pylint: disable=not-callable
def step_account_exists_and_is_signed_in(context, username):
    """Create one account and retain its authenticated browser client."""
    context.browser_client = _create_signed_in_client(username)


def _create_signed_in_client(username):
    """Create an account and authenticate through the website sign-in form."""
    password = "valid-password-123"
    User.objects.create_user(username=username, password=password)
    client = Client()
    response = client.post(
        "/login/",
        {"username": username, "password": password},
        follow=True,
    )
    assert response.status_code == 200
    assert "_auth_user_id" in client.session
    return client


@when('account "{username}" books seat "{seat_number}"')  # pylint: disable=not-callable
def step_account_books_seat(context, username, seat_number):
    """Let one account reserve a seat through the HTML workflow."""
    context.first_response = context.browser_clients[username].post(
        "/bookings/",
        {
            "movie": context.movie.pk,
            "seat": context.seats[seat_number].pk,
        },
        follow=True,
    )


@when('account "{username}" tries to book seat "{seat_number}"')  # pylint: disable=not-callable
def step_account_tries_to_book_seat(context, username, seat_number):
    """Submit a competing booking request from the second account."""
    context.second_response = context.browser_clients[username].post(
        "/bookings/",
        {
            "movie": context.movie.pk,
            "seat": context.seats[seat_number].pk,
        },
        follow=True,
    )


@then(  # pylint: disable=not-callable
    "the first booking succeeds and the second sees an "
    "unavailable-seat message"
)
def step_competing_request_is_rejected(context):
    """Assert only one booking exists and the losing user sees why."""
    first_page = context.first_response.content.decode().lower()
    second_page = context.second_response.content.decode().lower()
    assert "booking confirmed" in first_page
    assert "unavailable" in second_page
    booking_model = apps.get_model("bookings", "Booking")
    seat = context.seats["A1"]
    assert booking_model.objects.filter(seat=seat).count() == 1


@when(  # pylint: disable=not-callable
    'the signed-in visitor books seats "{first}" and "{second}"'
)
def step_signed_in_visitor_books_two_seats(context, first, second):
    """Submit separate booking requests for each available seat."""
    context.booking_responses = []
    for seat_number in (first, second):
        seat = context.seats[seat_number]
        response = context.browser_client.post(
            "/bookings/",
            {"movie": context.movie.pk, "seat": seat.pk},
            follow=True,
        )
        context.booking_responses.append(response)


@then("both distinct bookings are confirmed")  # pylint: disable=not-callable
def step_both_distinct_bookings_are_confirmed(context):
    """Verify both confirmations and independent persisted seat bookings."""
    for response in context.booking_responses:
        assert "booking confirmed" in response.content.decode().lower()
    booking_model = apps.get_model("bookings", "Booking")
    assert booking_model.objects.filter(
        user_id=context.browser_client.session["_auth_user_id"],
        movie=context.movie,
    ).count() == 2


@given(  # pylint: disable=not-callable
    'signed-in account "{username}" has 21 bookings and '
    'another user\'s booking'
)
def step_signed_in_account_has_paginated_history(context, username):
    """Seed 21 owned bookings plus one private booking for another user."""
    context.history_client = _create_signed_in_client(username)
    owner_id = context.history_client.session["_auth_user_id"]
    owner = User.objects.get(pk=owner_id)
    other_user = User.objects.create_user(
        username=f"{username}-other",
        password="valid-password-123",
    )
    movie = Movie.objects.create(  # pylint: disable=no-member
        title="History Feature",
        description="A movie used by booking history scenarios.",
        release_date="2026-10-08",
        duration=100,
    )
    booking_model = apps.get_model("bookings", "Booking")
    base_time = timezone.now()
    for index in range(21):
        seat = Seat.objects.create(  # pylint: disable=no-member
            movie=movie, seat_number=f"F{index:02d}"
        )
        booking = booking_model.objects.create(
            movie=movie,
            seat=seat,
            user=owner,
        )
        booking_model.objects.filter(pk=booking.pk).update(
            booking_date=base_time + timedelta(minutes=index)
        )
    private_seat = Seat.objects.create(  # pylint: disable=no-member
        movie=movie, seat_number="PRIVATE"
    )
    private_booking = booking_model.objects.create(
        movie=movie,
        seat=private_seat,
        user=other_user,
    )
    booking_model.objects.filter(pk=private_booking.pk).update(
        booking_date=base_time + timedelta(days=1)
    )


@given('signed-in account "{username}" has no bookings')  # pylint: disable=not-callable
def step_signed_in_account_has_no_bookings(context, username):
    """Create an authenticated account with no booking records."""
    context.history_client = _create_signed_in_client(username)


@when("the account opens booking history")  # pylint: disable=not-callable
def step_account_opens_booking_history(context):
    """Request the first page of the current account's booking history."""
    context.history_response = context.history_client.get("/bookings/history/")


@when("the account opens the next booking history page")  # pylint: disable=not-callable
def step_account_opens_next_booking_history_page(context):
    """Request the second page of the current account's booking history."""
    context.history_response = context.history_client.get(
        "/bookings/history/?page=2"
    )


@then(  # pylint: disable=not-callable
    "page one shows the 20 newest bookings without "
    "the other user's booking"
)
def step_history_page_one_is_private_and_newest(context):
    """Check newest-first page content, page size, and user isolation."""
    assert context.history_response.status_code == 200
    page = context.history_response.content.decode()
    assert all(f"F{index:02d}" in page for index in range(1, 21))
    assert "F00" not in page
    assert "PRIVATE" not in page
    assert page.index("F20") < page.index("F01")
    assert "page=2" in page


@then("page two shows the remaining booking without a next page")  # pylint: disable=not-callable
def step_history_page_two_has_remaining_booking(context):
    """Check the final booking appears on page two with no next link."""
    assert context.history_response.status_code == 200
    page = context.history_response.content.decode()
    assert "F00" in page
    assert "F20" not in page
    assert "PRIVATE" not in page
    assert "page=3" not in page


@then("the history page shows the empty state")  # pylint: disable=not-callable
def step_history_page_shows_empty_state(context):
    """Check a signed-in account without bookings sees an empty message."""
    assert context.history_response.status_code == 200
    page = context.history_response.content.decode().lower()
    assert "no bookings" in page or "no booking history" in page


@given('signed-in account "{username}" can manage movies')  # pylint: disable=not-callable
def step_signed_in_account_can_manage_movies(context, username):
    """Create a signed-in API client for catalog-management requests."""
    context.catalog_user = User.objects.create_user(
        username=username,
        password="valid-password-123",
    )
    context.catalog_client = APIClient()
    context.catalog_client.force_login(context.catalog_user)


@when('the catalog manager creates movie "{title}"')  # pylint: disable=not-callable
def step_catalog_manager_creates_movie(context, title):
    """Create a movie through the authenticated movie API."""
    context.catalog_response = context.catalog_client.post(
        "/api/movies/",
        {
            "title": title,
            "description": "A movie created by a catalog workflow.",
            "release_date": "2026-10-08",
            "duration": 120,
        },
        format="json",
    )


@then("the movie is created successfully")  # pylint: disable=not-callable
def step_movie_is_created_successfully(context):
    """Retain the created movie ID for update and delete steps."""
    assert context.catalog_response.status_code == 201
    context.catalog_movie_id = context.catalog_response.json()["id"]


@when('the catalog manager updates the movie title to "{title}"')  # pylint: disable=not-callable
def step_catalog_manager_updates_movie(context, title):
    """Patch the movie title through the authenticated catalog API."""
    context.catalog_response = context.catalog_client.patch(
        f"/api/movies/{context.catalog_movie_id}/",
        {"title": title},
        format="json",
    )


@then("the movie update is visible in the public catalog")  # pylint: disable=not-callable
def step_movie_update_is_public(context):
    """Check the update response and public movie collection."""
    assert context.catalog_response.status_code == 200
    context.catalog_movie_title = context.catalog_response.json()["title"]
    public_response = APIClient().get("/api/movies/")
    assert any(
        movie["id"] == context.catalog_movie_id
        and movie["title"] == context.catalog_movie_title
        for movie in public_response.json()
    )


@when("the catalog manager deletes the movie")  # pylint: disable=not-callable
def step_catalog_manager_deletes_movie(context):
    """Delete the unbooked movie through the catalog API."""
    context.catalog_response = context.catalog_client.delete(
        f"/api/movies/{context.catalog_movie_id}/"
    )


@then("the movie is no longer in the catalog")  # pylint: disable=not-callable
def step_movie_is_deleted(context):
    """Verify deletion succeeded and public detail now returns not-found."""
    assert context.catalog_response.status_code == 204
    detail_response = APIClient().get(
        f"/api/movies/{context.catalog_movie_id}/"
    )
    assert detail_response.status_code == 404


@given('signed-in account "{username}" has a movie with booking history')  # pylint: disable=not-callable
def step_catalog_manager_has_booked_movie(context, username):
    """Create a protected movie, seat, and booking for the catalog manager."""
    step_signed_in_account_can_manage_movies(context, username)
    context.protected_movie = Movie.objects.create(  # pylint: disable=no-member
        title="Protected by history",
        description="A movie that must remain while it has bookings.",
        release_date="2026-10-08",
        duration=120,
    )
    protected_seat = Seat.objects.create(  # pylint: disable=no-member
        movie=context.protected_movie,
        seat_number="A1",
    )
    booking_model = apps.get_model("bookings", "Booking")
    booking_model.objects.create(
        movie=context.protected_movie,
        seat=protected_seat,
        user=context.catalog_user,
    )


@when("the catalog manager deletes that movie")  # pylint: disable=not-callable
def step_catalog_manager_deletes_protected_movie(context):
    """Attempt to delete a movie that already has booking history."""
    context.catalog_response = context.catalog_client.delete(
        f"/api/movies/{context.protected_movie.pk}/"
    )


@then(  # pylint: disable=not-callable
    "deletion is rejected and the booking history is preserved"
)
def step_movie_delete_is_rejected_with_history(context):
    """Check the conflict response and ensure the booking remains."""
    assert context.catalog_response.status_code == 409
    assert Movie.objects.filter(pk=context.protected_movie.pk).exists()
    booking_model = apps.get_model("bookings", "Booking")
    booking_count = booking_model.objects.filter(
        movie=context.protected_movie
    ).count()
    assert booking_count == 1


@given('movie "{title}" exists')  # pylint: disable=not-callable
def step_movie_exists_for_anonymous_catalog(context, title):
    """Create a public movie for anonymous write-rejection checks."""
    context.anonymous_movie = Movie.objects.create(  # pylint: disable=no-member
        title=title,
        description="A movie for anonymous-write tests.",
        release_date="2026-10-08",
        duration=120,
    )


@when(  # pylint: disable=not-callable
    "an anonymous visitor attempts movie create update and delete requests"
)
def step_anonymous_catalog_writes(context):
    """Try protected movie mutations without an authenticated session."""
    client = APIClient()
    context.anonymous_write_responses = [
        client.post(
            "/api/movies/",
            {
                "title": "Anonymous Creation",
                "description": "Should not be created.",
                "release_date": "2026-10-08",
                "duration": 100,
            },
            format="json",
        ),
        client.patch(
            f"/api/movies/{context.anonymous_movie.pk}/",
            {"title": "Anonymous Change"},
            format="json",
        ),
        client.delete(f"/api/movies/{context.anonymous_movie.pk}/"),
    ]


@then(  # pylint: disable=not-callable
    "all anonymous movie writes are rejected and the movie remains unchanged"
)
def step_anonymous_writes_are_rejected(context):
    """Verify permission responses and the unchanged public record."""
    assert all(
        response.status_code == 403
        for response in context.anonymous_write_responses
    )
    context.anonymous_movie.refresh_from_db()
    assert context.anonymous_movie.title == "Protected Catalog Movie"
    assert not Movie.objects.filter(title="Anonymous Creation").exists()


@given('signed-in account "{username}" can manage seats')  # pylint: disable=not-callable
def step_signed_in_account_can_manage_seats(context, username):
    """Create a signed-in seat inventory editor."""
    context.seat_manager = User.objects.create_user(
        username=username,
        password="valid-password-123",
    )
    context.seat_manager_client = APIClient()
    context.seat_manager_client.force_login(context.seat_manager)


@when('the seat manager adds seat "{seat_number}"')  # pylint: disable=not-callable
def step_seat_manager_adds_seat(context, seat_number):
    """Create one inventory record through the seat API."""
    context.seat_response = context.seat_manager_client.post(
        "/api/seats/",
        {"movie": context.movie.pk, "seat_number": seat_number},
        format="json",
    )
    assert context.seat_response.status_code == 201
    context.managed_seat = Seat.objects.get(
        pk=context.seat_response.json()["id"]
    )
    context.seats[seat_number] = context.managed_seat


@when('the seat manager tries to add duplicate seat "{seat_number}"')  # pylint: disable=not-callable
def step_seat_manager_adds_duplicate_seat(context, seat_number):
    """Attempt to add a seat label already used by the movie."""
    context.duplicate_seat_response = context.seat_manager_client.post(
        "/api/seats/",
        {"movie": context.movie.pk, "seat_number": seat_number},
        format="json",
    )


@when('another account books seat "{seat_number}"')  # pylint: disable=not-callable
def step_another_account_books_inventory_seat(context, seat_number):
    """Book a managed seat as a different authenticated user."""
    context.seat_booker = User.objects.create_user(
        username="seat-inventory-booker",
        password="valid-password-123",
    )
    context.seat_booker_client = APIClient()
    context.seat_booker_client.force_login(context.seat_booker)
    context.booking_response = context.seat_booker_client.post(
        "/api/bookings/",
        {
            "movie": context.movie.pk,
            "seat": context.seats[seat_number].pk,
        },
        format="json",
    )


@when('the seat manager deletes seat "{seat_number}"')  # pylint: disable=not-callable
def step_seat_manager_deletes_seat(context, seat_number):
    """Delete a seat from the manager's movie inventory."""
    seat = context.seats[seat_number]
    context.seat_delete_response = context.seat_manager_client.delete(
        f"/api/seats/{seat.pk}/"
    )


@when('an anonymous visitor attempts to add seat "{seat_number}"')  # pylint: disable=not-callable
def step_anonymous_visitor_adds_seat(context, seat_number):
    """Attempt to create movie inventory without signing in."""
    context.anonymous_seat_number = seat_number
    context.anonymous_seat_response = APIClient().post(
        "/api/seats/",
        {"movie": context.movie.pk, "seat_number": seat_number},
        format="json",
    )


@then('seat "{seat_number}" is added and can be booked by the other account')  # pylint: disable=not-callable
def step_added_seat_is_booked_by_other_account(context, seat_number):
    """Verify the new seat is public inventory and another user booked it."""
    assert context.seat_response.status_code == 201
    assert context.seat_response.json()["status"] == Seat.STATUS_AVAILABLE
    assert context.booking_response.status_code == 201
    seat = Seat.objects.get(pk=context.seats[seat_number].pk)
    seat.refresh_from_db()
    assert seat.status == Seat.STATUS_RESERVED
    assert Booking.objects.filter(seat=seat, user=context.seat_booker).exists()


@then("the duplicate seat number is rejected")  # pylint: disable=not-callable
def step_duplicate_seat_is_rejected(context):
    """Check the duplicate error is attached to the seat label."""
    assert context.duplicate_seat_response.status_code == 400
    assert "seat_number" in context.duplicate_seat_response.json()
    assert Seat.objects.filter(movie=context.movie).count() == 3


@then("the booked seat deletion is rejected")  # pylint: disable=not-callable
def step_booked_seat_deletion_is_rejected(context):
    """Verify the API preserves both the booked seat and its booking."""
    assert context.booking_response.status_code == 201
    assert context.seat_delete_response.status_code == 409
    assert Seat.objects.filter(pk=context.managed_seat.pk).exists()
    assert Booking.objects.filter(seat=context.managed_seat).exists()


@then("anonymous seat creation is rejected without changing inventory")  # pylint: disable=not-callable
def step_anonymous_seat_creation_is_rejected(context):
    """Check permission failure and absence of anonymous inventory changes."""
    assert context.anonymous_seat_response.status_code == 403
    assert not Seat.objects.filter(
        movie=context.movie,
        seat_number=context.anonymous_seat_number,
    ).exists()
