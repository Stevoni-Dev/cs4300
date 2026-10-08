"""Integration tests for authenticated seat inventory API behavior."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookings.models import Booking, Movie, Seat


User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestSeatCrudApi:
    """Exercise public reads and authenticated seat CRUD operations."""

    @pytest.fixture
    def user(self):
        """Create the signed-in inventory editor account."""
        return User.objects.create_user(
            username="seat-inventory-editor",
            password="valid-password-123",
        )

    @pytest.fixture
    def movies(self):
        """Create two movies for inventory ownership and cascade checks."""
        first = Movie.objects.create(
            title="Arrival",
            description="A linguist decodes a mysterious signal.",
            release_date="2016-11-11",
            duration=116,
        )
        second = Movie.objects.create(
            title="Moonlight",
            description="A coming-of-age drama.",
            release_date="2016-10-21",
            duration=111,
        )
        return first, second

    def test_signed_in_user_can_create_retrieve_update_and_delete_seat(
        self, user, movies
    ):
        """CRUD responses preserve server-owned status and public visibility.
        """
        movie, _ = movies
        client = APIClient()
        client.force_login(user)

        create = client.post(
            "/api/seats/",
            {
                "movie": movie.pk,
                "seat_number": "A1",
                "status": "reserved",
            },
            format="json",
        )
        assert create.status_code == 201
        assert create.json()["status"] == Seat.STATUS_AVAILABLE
        seat_id = create.json()["id"]

        created_list = APIClient().get(
            "/api/seats/", {"movie": movie.pk}
        )
        assert created_list.status_code == 200
        assert [item["seat_number"] for item in created_list.json()] == [
            "A1"
        ]
        assert b"A1" in APIClient().get(
            f"/movies/{movie.pk}/"
        ).content

        retrieve = client.get(f"/api/seats/{seat_id}/")
        assert retrieve.status_code == 200
        assert retrieve.json()["seat_number"] == "A1"

        replace = client.put(
            f"/api/seats/{seat_id}/",
            {
                "movie": movie.pk,
                "seat_number": "A2",
                "status": "reserved",
            },
            format="json",
        )
        assert replace.status_code == 200
        assert replace.json()["seat_number"] == "A2"
        assert replace.json()["status"] == Seat.STATUS_AVAILABLE

        patch = client.patch(
            f"/api/seats/{seat_id}/",
            {"seat_number": "A3"},
            format="json",
        )
        assert patch.status_code == 200
        assert patch.json()["seat_number"] == "A3"

        public_list = APIClient().get("/api/seats/", {"movie": movie.pk})
        assert public_list.status_code == 200
        assert [item["seat_number"] for item in public_list.json()] == ["A3"]
        detail_page = APIClient().get(f"/movies/{movie.pk}/")
        assert detail_page.status_code == 200
        assert b"A3" in detail_page.content
        assert b"A1" not in detail_page.content

        delete = client.delete(f"/api/seats/{seat_id}/")
        assert delete.status_code == 204
        assert not Seat.objects.filter(pk=seat_id).exists()
        assert APIClient().get(
            "/api/seats/", {"movie": movie.pk}
        ).json() == []
        deleted_page = APIClient().get(f"/movies/{movie.pk}/")
        assert b"A3" not in deleted_page.content

    @pytest.mark.parametrize(
        "payload",
        [
            {"seat_number": "A1"},
            {"movie": "not-an-id", "seat_number": "A1"},
        ],
    )
    def test_create_rejects_missing_or_malformed_movie(self, user, payload):
        """Movie is mandatory and malformed primary keys return 400."""
        client = APIClient()
        client.force_login(user)

        response = client.post("/api/seats/", payload, format="json")

        assert response.status_code == 400
        assert "movie" in response.json()
        assert Seat.objects.count() == 0

    def test_create_returns_not_found_for_unknown_movie(self, user):
        """A well-formed but absent movie identifier returns 404."""
        client = APIClient()
        client.force_login(user)

        response = client.post(
            "/api/seats/",
            {"movie": 999999, "seat_number": "A1"},
            format="json",
        )

        assert response.status_code == 404
        assert Seat.objects.count() == 0

    def test_update_ignores_movie_and_duplicate_or_invalid_numbers_are_errors(
        self, user, movies
    ):
        """Seat labels are validated within their original movie inventory."""
        movie, other_movie = movies
        first = Seat.objects.create(movie=movie, seat_number="A1")
        second = Seat.objects.create(movie=movie, seat_number="A2")
        client = APIClient()
        client.force_login(user)

        duplicate = client.patch(
            f"/api/seats/{second.pk}/",
            {"seat_number": "A1"},
            format="json",
        )
        assert duplicate.status_code == 400
        assert "seat_number" in duplicate.json()

        for invalid_number in ("  ", "A" * 11, 123):
            invalid_create = client.post(
                "/api/seats/",
                {"movie": movie.pk, "seat_number": invalid_number},
                format="json",
            )
            assert invalid_create.status_code == 400
            assert "seat_number" in invalid_create.json()

            invalid = client.patch(
                f"/api/seats/{second.pk}/",
                {"seat_number": invalid_number},
                format="json",
            )
            assert invalid.status_code == 400
            assert "seat_number" in invalid.json()

        move_attempt = client.patch(
            f"/api/seats/{first.pk}/",
            {"movie": other_movie.pk, "seat_number": "A1-renamed"},
            format="json",
        )
        assert move_attempt.status_code == 200
        first.refresh_from_db()
        assert first.movie == movie

    def test_same_seat_number_is_allowed_for_a_different_movie(
        self, user, movies
    ):
        """The uniqueness rule applies to a movie's own inventory only."""
        first_movie, second_movie = movies
        Seat.objects.create(movie=first_movie, seat_number="A1")
        client = APIClient()
        client.force_login(user)

        response = client.post(
            "/api/seats/",
            {"movie": second_movie.pk, "seat_number": "A1"},
            format="json",
        )

        assert response.status_code == 201
        assert response.json()["seat_number"] == "A1"

    def test_unknown_seat_retrieve_update_and_delete_return_not_found(
        self, user
    ):
        """All detail actions return 404 for absent seat identifiers."""
        client = APIClient()
        client.force_login(user)

        retrieve = client.get("/api/seats/999999/")
        update = client.patch(
            "/api/seats/999999/",
            {"seat_number": "A1"},
            format="json",
        )
        delete = client.delete("/api/seats/999999/")

        assert [
            retrieve.status_code,
            update.status_code,
            delete.status_code,
        ] == [404, 404, 404]

    def test_anonymous_writes_are_rejected_and_reads_remain_public(
        self, movies
    ):
        """Public inventory remains readable without enabling anonymous writes.
        """
        movie, _ = movies
        seat = Seat.objects.create(movie=movie, seat_number="A1")
        client = APIClient()

        create = client.post(
            "/api/seats/",
            {"movie": movie.pk, "seat_number": "A2"},
            format="json",
        )
        update = client.patch(
            f"/api/seats/{seat.pk}/",
            {"seat_number": "A3"},
            format="json",
        )
        delete = client.delete(f"/api/seats/{seat.pk}/")
        public_list = client.get("/api/seats/", {"movie": movie.pk})
        public_detail = client.get(f"/api/seats/{seat.pk}/")

        assert create.status_code == 403
        assert update.status_code == 403
        assert delete.status_code == 403
        assert public_list.status_code == 200
        assert public_detail.status_code == 200
        assert Seat.objects.filter(
            pk=seat.pk,
            seat_number="A1",
        ).exists()
        assert Seat.objects.count() == 1

    def test_session_authenticated_invalid_csrf_does_not_mutate_inventory(
        self, user, movies
    ):
        """Session-authenticated writes enforce DRF's CSRF validation.
        """
        movie, _ = movies
        seat = Seat.objects.create(movie=movie, seat_number="A1")
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)

        create = client.post(
            "/api/seats/",
            {"movie": movie.pk, "seat_number": "A2"},
            format="json",
        )
        update = client.patch(
            f"/api/seats/{seat.pk}/",
            {"seat_number": "A3"},
            format="json",
        )
        delete = client.delete(f"/api/seats/{seat.pk}/")

        assert all(
            response.status_code == 403
            and response.json()["detail"].startswith("CSRF Failed:")
            for response in (create, update, delete)
        )
        assert Seat.objects.count() == 1
        seat.refresh_from_db()
        assert seat.seat_number == "A1"

    def test_booked_seat_delete_conflicts_and_preserves_history(
        self, user, movies
    ):
        """A booked seat cannot be deleted through the inventory API."""
        movie, _ = movies
        seat = Seat.objects.create(movie=movie, seat_number="A1")
        booking = Booking.objects.create(movie=movie, seat=seat, user=user)
        client = APIClient()
        client.force_login(user)

        response = client.delete(f"/api/seats/{seat.pk}/")

        assert response.status_code == 409
        assert Seat.objects.filter(pk=seat.pk).exists()
        assert Booking.objects.filter(pk=booking.pk, seat=seat).exists()

    def test_deleting_movie_removes_its_unbooked_seats(self, user, movies):
        """Existing movie cascade behavior removes unbooked seat inventory."""
        movie, _ = movies
        Seat.objects.create(movie=movie, seat_number="A1")
        client = APIClient()
        client.force_login(user)

        response = client.delete(f"/api/movies/{movie.pk}/")

        assert response.status_code == 204
        assert not Seat.objects.filter(movie=movie).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_existing_seat_list_query_contract_is_unchanged():
    """Missing, invalid, unknown, and empty movie seat reads stay stable."""
    client = APIClient()
    movie = Movie.objects.create(
        title="Empty inventory",
        description="No seats have been added.",
        release_date="2026-10-08",
        duration=100,
    )

    assert client.get("/api/seats/").status_code == 400
    assert client.get("/api/seats/", {"movie": "invalid"}).status_code == 400
    assert client.get("/api/seats/", {"movie": 999999}).status_code == 404
    empty = client.get("/api/seats/", {"movie": movie.pk})
    assert empty.status_code == 200
    assert empty.json() == []
    assert client.get(f"/api/seats/{999999}/").status_code == 404
