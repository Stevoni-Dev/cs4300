# API Contract: Movie Theater Booking

Base path: `/api/`. Responses use JSON. Movie and seat reads are available to visitors;
all writes require the signed-in single user role. Booking creation and booking history
require sign-in. Protected endpoints use DRF's configured authentication and permission
classes with its default exception handling. The status, authentication challenge header,
and error body for unauthenticated or forbidden requests follow the behavior of those DRF
classes; this contract does not normalize them to a project-specific response. Browser-
session API mutations require a valid CSRF token.

## Movies

### `GET /api/movies/`

List movies. Returns `200` and an array (or DRF paginated result if pagination is
configured) containing `id`, `title`, `description`, `release_date`, and `duration`.

### `POST /api/movies/`

Create a movie. Requires sign-in; unauthenticated requests receive DRF's response for
the configured authentication and permission classes. Request fields: `title`, `description`, `release_date`
(ISO date), and `duration` (positive whole minutes). Returns `201` and the created movie;
invalid fields return `400` with field-specific errors.

### `GET /api/movies/{movie_id}/`

Retrieve one movie. Returns `200`; an unknown id returns `404`.

### `PUT` / `PATCH /api/movies/{movie_id}/`

Replace or partially update a movie. Requires sign-in; unauthenticated requests receive
DRF's response for the configured authentication and permission classes. Returns `200`; invalid values return `400`, unknown id
returns `404`.

### `DELETE /api/movies/{movie_id}/`

Delete a movie with no booking history. Requires sign-in; unauthenticated requests receive
DRF's response for the configured authentication and permission classes. Returns `204` and
removes the movie's seat inventory with it; deletion is rejected with `409` if any
booking history exists, and unknown id returns `404`.

## Seats

A seat belongs to exactly one movie, and its `seat_number` is unique within that movie
(the same number may exist for different movies). Seat responses contain `id`, `movie`,
`seat_number`, and `status` (`available` or `reserved`). `/api/seats/` is the only seat
endpoint; there are no movie-nested seat routes.

### `GET /api/seats/?movie={movie_id}`

List seats and their current status for one movie. Public. The `movie` query parameter is
required. Returns `200` with a seat array. Missing or invalid `movie` returns `400`; an
unknown movie returns `404`.

### `GET /api/seats/{seat_id}/`

Retrieve one seat and its status. Public. Returns `200` or `404`.

### `POST /api/seats/`

Create a seat. Requires sign-in; unauthenticated requests receive DRF's response for the
configured authentication and permission classes. Request body:

```json
{
  "movie": 12,
  "seat_number": "A1"
}
```

`movie` and `seat_number` are required. `seat_number` must be non-blank and unique within
the movie. The server sets `status` to `available`; a client-supplied `status` is ignored.
Returns `201` and the created seat. A missing or malformed `movie`, or a missing, blank,
invalid, or duplicate `seat_number`, returns `400` with a field-specific error and creates
no seat. An unknown movie returns `404`, as for booking requests.

### `PUT` / `PATCH /api/seats/{seat_id}/`

Change a seat's `seat_number`. Requires sign-in; unauthenticated requests receive DRF's
response for the configured authentication and permission classes. Validation matches
creation, and renaming a seat to its own current number is valid. `movie` and `status` are
read-only on update; client-supplied values are ignored, so a seat cannot move to another
movie. Returns `200`; invalid or duplicate values return `400`, and an unknown seat
returns `404`.

### `DELETE /api/seats/{seat_id}/`

Delete a seat with no booking history. Requires sign-in; unauthenticated requests receive
DRF's response for the configured authentication and permission classes. Returns `204`;
deletion is rejected with `409` if the seat has a booking, leaving the seat and its
booking intact. An unknown seat returns `404`.

## Bookings

### `GET /api/bookings/`

Return the signed-in user's booking history only. Each item contains `id`, `movie`,
`seat`, `booking_date`, plus read-only display details needed to render the movie title
and seat number. Results are ordered by `booking_date` newest first and use page-number
pagination with 20 bookings per page, selected with the `page` query parameter. The
response contains `count`, `next`, `previous`, and `results`. An empty history returns
`count: 0` and `results: []`. Unauthenticated requests receive DRF's response for the
configured authentication and permission classes without returning booking data.

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
success. An unauthenticated request receives DRF's response for the configured
authentication and permission classes. Returns `404` if the movie or seat does not exist,
`400` if the movie and seat exist but the seat belongs to another movie or other request
fields are invalid, `403` for invalid CSRF on an authenticated session, and `409` when
another request has already reserved the seat. A failed request creates no booking.

Each booking request reserves exactly one seat. A signed-in user may submit multiple
booking requests for different available seats for the same movie. A seat already
reserved by any user cannot be booked again.

Booking update and deletion are not exposed in phase one, preserving booking history.

## Shared error expectations

- Validation errors identify the invalid field or explain the failed booking rule.
- Missing resources return `404`, including an unknown `movie` on seat creation.
- Deleting a movie or seat with booking history returns `409`.
- Authentication and permission failures use the status, challenge header, and error body produced by the configured DRF classes and default exception handler.
- Invalid CSRF on an authenticated session is rejected by DRF; the request does not perform the mutation.
- Seat conflicts return `409` and an actionable unavailable-seat message.
- Unauthorized requests never reveal another user's bookings.
- HTML forms use the same rules and booking service; their presentation differs, not
  their persisted data or reservation outcomes.