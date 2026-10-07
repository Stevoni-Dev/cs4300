# API Contract: Movie Theater Booking

Base path: `/api/`. Responses use JSON. Movie and seat reads are available to visitors;
all writes require the signed-in single user role. Booking creation and booking history
require sign-in. Protected endpoints use the default Django REST Framework authentication
behavior: unauthenticated requests return `401 Unauthorized`, and authenticated requests
rejected for permissions or CSRF reasons return `403 Forbidden`. Browser-session API
mutations require a valid CSRF token.

## Movies

### `GET /api/movies/`

List movies. Returns `200` and an array (or DRF paginated result if pagination is
configured) containing `id`, `title`, `description`, `release_date`, and `duration`.

### `POST /api/movies/`

Create a movie. Requires sign-in; unauthenticated requests receive the standard DRF
`401` response. Request fields: `title`, `description`, `release_date`
(ISO date), and `duration` (positive whole minutes). Returns `201` and the created movie;
invalid fields return `400` with field-specific errors.

### `GET /api/movies/{movie_id}/`

Retrieve one movie. Returns `200`; an unknown id returns `404`.

### `PUT` / `PATCH /api/movies/{movie_id}/`

Replace or partially update a movie. Requires sign-in; unauthenticated requests receive
the standard DRF `401` response. Returns `200`; invalid values return `400`, unknown id
returns `404`.

### `DELETE /api/movies/{movie_id}/`

Delete a movie with no booking history. Requires sign-in; unauthenticated requests receive
the standard DRF `401` response. Returns `204`; deletion is rejected with `409` if any
booking history exists, and unknown id returns `404`.

## Seats

### `GET /api/seats/?movie={movie_id}`

List seats and their current status for one movie. The `movie` query parameter is
required. Returns `200` with items containing `id`, `movie`, `seat_number`, and
`status` (`available` or `reserved`). Missing or invalid `movie` returns `400`; an
unknown movie returns `404`.

### `GET /api/seats/{seat_id}/`

Retrieve one seat and its status. Returns `200` or `404`. Seat creation and mutation are
not part of the user-facing API in phase one; inventory is provisioned separately.

## Bookings

### `GET /api/bookings/`

Return the signed-in user's booking history only. Each item contains `id`, `movie`,
`seat`, `booking_date`, plus read-only display details needed to render the movie title
and seat number. Results are ordered by `booking_date` newest first and use page-number
pagination with 20 bookings per page, selected with the `page` query parameter. The
response contains `count`, `next`, `previous`, and `results`. An empty history returns
`count: 0` and `results: []`. Unauthenticated requests receive the standard DRF `401`
response without returning booking data.

### `POST /api/bookings/`

Create a booking for the authenticated user. Request body:

```json
{
  "movie": 12,
  "seat": 47
}
```

The server sets `user` and `booking_date`; clients cannot override them. The seat must
belong to the requested movie and be available. Returns `201` and the booking on
success. Returns `401` for unauthenticated requests, `404` if the movie or seat does not
exist, `400` if the movie and seat exist but the seat belongs to another movie or other
request fields are invalid, `403` for invalid CSRF on an authenticated session, and
`409` when another request has already reserved the seat. A failed request creates no
booking.

Each booking request reserves exactly one seat. A signed-in user may submit multiple
booking requests for different available seats for the same movie. A seat already
reserved by any user cannot be booked again.

Booking update and deletion are not exposed in phase one, preserving booking history.

## Shared error expectations

- Validation errors identify the invalid field or explain the failed booking rule.
- Missing resources return `404`.
- Unauthenticated access to protected endpoints returns `401` using the framework default payload.
- Authenticated requests rejected for authorization or CSRF reasons return `403`.
- Seat conflicts return `409` and an actionable unavailable-seat message.
- Unauthorized requests never reveal another user's bookings.
- HTML forms use the same rules and booking service; their presentation differs, not
  their persisted data or reservation outcomes.