"""Project-level URL routing.

This file exposes administrative routes and delegates app-specific routes to
the ``bookings`` application, keeping movie listings and booking endpoints in
their own module rather than the project root.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Keep Django admin available for development and deployment checks.
    path("admin/", admin.site.urls),
    # Mount app routes at the root to preserve their expected public paths.
    path("", include("bookings.urls")),
]
