"""Shared DRF API helpers for the bookings app."""

from __future__ import annotations

from rest_framework import exceptions
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    """Normalize DRF auth failures to the project contract.

    Anonymous requests to protected endpoints must be 401 with the expected
    JSON error shape, while authenticated forbidden requests (including invalid
    CSRF) remain 403.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
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
        response.status_code = 401
        response.data = {
            "detail": "Authentication credentials were not provided."
        }
        return response

    if isinstance(exc, exceptions.PermissionDenied):
        if not is_authenticated:
            response.status_code = 401
            response.data = {
                "detail": "Authentication credentials were not provided."
            }
            return response

    return response
