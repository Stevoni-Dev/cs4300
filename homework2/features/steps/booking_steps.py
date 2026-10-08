"""Smoke-step definitions for the Behave-Django test harness."""

from __future__ import annotations

import re

from behave import given, then, when
from django.apps import apps
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client

from bookings.models import Movie, Seat


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


@when('the visitor registers with username "{username}" and password "{password}"')  # pylint: disable=not-callable
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


@when('the visitor submits valid CSRF-protected registration data for "{username}"')  # pylint: disable=not-callable
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


@when('the visitor signs in with username "{username}" and password "{password}"')  # pylint: disable=not-callable
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


@then("the first booking succeeds and the second sees an unavailable-seat message")  # pylint: disable=not-callable
def step_competing_request_is_rejected(context):
    """Assert only one booking exists and the losing user sees why."""
    first_page = context.first_response.content.decode().lower()
    second_page = context.second_response.content.decode().lower()
    assert "booking confirmed" in first_page
    assert "unavailable" in second_page
    booking_model = apps.get_model("bookings", "Booking")
    seat = context.seats["A1"]
    assert booking_model.objects.filter(seat=seat).count() == 1


@when('the signed-in visitor books seats "{first}" and "{second}"')  # pylint: disable=not-callable
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
