"""URL declarations for the bookings app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import MovieViewSet, SeatViewSet
from .views import movie_detail_view, movie_list_view

router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"seats", SeatViewSet, basename="seat")

urlpatterns = [
    path("api/", include(router.urls)),
    path("movies/", movie_list_view, name="movie-list"),
    path("movies/<int:pk>/", movie_detail_view, name="movie-detail"),
]
