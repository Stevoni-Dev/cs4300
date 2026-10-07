"""Project-level URL routing.

This file exposes administrative routes and delegates the app-specific routes to the
``bookings`` application, allowing the movie listings and booking endpoints to live in
an app-specific module rather than the project root.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin is kept available during development and deployment checks.
    path("admin/", admin.site.urls),
    # The application-level routes are mounted at the root so they can be served at the
    # expected public paths without a duplicate namespace.
    path("", include("bookings.urls")),
]
