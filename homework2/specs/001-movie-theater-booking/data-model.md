# Data Model: Movie Theater Booking

## Movie

Represents a listed, bookable movie. In phase one a movie is the booking event and has
exactly one seat inventory; there are no showtime or auditorium entities.

| Field | Meaning | Constraints |
|-------|---------|-------------|
| `id` | Stable movie identifier | Primary key |
| `title` | Display title | Required, non-empty, bounded length |
| `description` | Listing description | Required |
| `release_date` | Release date | Required date |
| `duration` | Runtime in minutes | Required positive integer |

Relationships: one movie has many seats and may have many bookings. Deleting a movie
with booking history is rejected to preserve reservations; deleting an unbooked movie
may remove its seat inventory.

## Seat

Represents one numbered seat in a movie's single inventory.

| Field | Meaning | Constraints |
|-------|---------|-------------|
| `id` | Stable seat identifier | Primary key |
| `movie` | Owning movie | Required foreign key |
| `seat_number` | Human-readable seat label | Required; unique within a movie |
| `status` | Current booking state | `available` or `reserved`; initially available |

Invariant: `(movie, seat_number)` is unique. In phase one the status transition is
`available -> reserved`; cancellation and reopening a seat are out of scope.

## Booking

Represents one confirmed reservation.

| Field | Meaning | Constraints |
|-------|---------|-------------|
| `id` | Stable booking identifier | Primary key |
| `movie` | Booked movie | Required foreign key |
| `seat` | Reserved seat | Required one-to-one relation; at most one booking per seat |
| `user` | Booking owner | Required foreign key to Django's user model |
| `booking_date` | Time the booking was recorded | Set by the server; read-only to clients |

Invariants:

- A booking's seat must belong to its movie; validate this in the shared booking
  service/serializer before writing.
- The booking's user is always the authenticated request user; clients cannot choose
  another user.
- Booking creation and the seat status update are one atomic operation. A failure in
  either write rolls back both.
- The one-to-one seat relation and the seat's reserved state prevent a second booking.
- A user may have multiple bookings for the same movie, provided each booking is for a
  different available seat; there is no per-user/per-movie booking cap.
- Booking history queries are filtered by the authenticated user before serialization.

## User

Use Django's built-in user identity and password handling. Phase one exposes only one
user role. Registration and sign-in use username/password unless the implementation
finds an assignment constraint requiring a different field set. User identifiers and
password data are never accepted as booking ownership from API clients.

## Booking lifecycle

1. A visitor registers and signs in, or an existing user signs in.
2. The user selects a movie and an available seat.
3. The shared booking operation atomically claims the available seat and creates the
   booking for the authenticated user.
4. On success, seat status is `reserved` and booking history includes the new record.
5. If the seat has already been claimed, the operation creates no booking and reports
   that the seat is unavailable.