"""URL declarations for the bookings app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import BookingViewSet, MovieViewSet, SeatViewSet
from .views import (
    login_view,
    movie_detail_view,
    movie_list_view,
    registration_view,
)

router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"seats", SeatViewSet, basename="seat")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("api/", include(router.urls)),
    path("movies/", movie_list_view, name="movie-list"),
    path("movies/<int:pk>/", movie_detail_view, name="movie-detail"),
    path("register/", registration_view, name="register"),
    path("login/", login_view, name="login"),
]
