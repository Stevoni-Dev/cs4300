# Quickstart and Validation: Movie Theater Booking

## Prerequisites

- Python 3.12 and `pip`
- A terminal in the repository root
- For Render deployment: a Render account with access to a managed PostgreSQL database

## Local development in DevEdu

1. Create and activate a virtual environment using the course environment instructions.
2. Install the pinned project dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`, set a local `SECRET_KEY`, and keep `.env` untracked.
4. Initialize the database and start the service on the required port:

   ```sh
   python manage.py migrate
   python manage.py runserver 0.0.0.0:3000
   ```

5. Open the DevEdu forwarded port 3000. Register a user, browse movies, inspect seat
   availability, make a booking, and review booking history. The HTML pages and API must
   show the same database state.

## Automated tests

The constitution requires a test to be written and observed failing before each behavior
is implemented. Every Django test is tagged exactly `unit` or `integration`; every
Behave workflow is tagged `@integration`.

```sh
python manage.py test --tag=unit
python manage.py test --tag=integration
python manage.py behave --tags=integration
```

Expected outcomes: each command exits successfully; unit tests cover isolated model, serializer, and reservation-service rules; integration tests cover API status codes, authentication, CSRF, persistence, templates, user-scoped history, and booking conflicts. A transaction-backed integration test must synchronize two requests for the same available seat on separate database connections and assert one `201`, one `409`, and exactly one persisted booking. Behave scenarios demonstrate registration/sign-in, browsing, booking, and history as end-to-end user workflows.

## API smoke checks

With the local server running:

- `GET /api/movies/` lists the same movies displayed on the movie page.
- `GET /api/seats/?movie=<id>` displays the same availability as the seat page.
- Sign in, include the session cookie and CSRF token, then `POST /api/bookings/` with
  `movie` and `seat`; expect `201` for the first reservation.
- Submit the same seat again; expect `409` and no second booking.
- `GET /api/bookings/` returns only the signed-in user's history, newest first, with up
   to 20 bookings per page; use `?page=2` for the next page. An account with no bookings
   receives `count: 0` and `results: []`.
- Authenticated `POST`, `PUT`, `PATCH`, and eligible `DELETE` requests to `/api/movies/`
  exercise movie CRUD; anonymous writes are rejected.

## Manual UI review

Use keyboard-only navigation and a narrow viewport to verify readable movie details,
distinguishable seat states, visible focus, usable registration/sign-in and booking
controls, empty states, and clear success/conflict feedback.

## Render deployment validation

1. Configure the Render web service and managed PostgreSQL database from `render.yaml`;
   provide the database connection through the `DATABASE_URL` environment variable.
2. Set `SECRET_KEY`, `DEBUG=False`, allowed hosts, and trusted CSRF origins as Render
   environment variables. Never commit production secrets or database credentials.
3. Build installs dependencies and runs `collectstatic`; release/start setup applies
   migrations and starts Gunicorn using `movie_theater_booking.wsgi:application`.
4. Confirm the cold-started service becomes ready within its configured startup/readiness window. Create a booking, restart the app service, and verify the booking remains in the signed-in user's history.
5. Keep the assignment deployment to one application instance; PostgreSQL provides the persistent shared database.

## Documentation check

Before submission, follow the README from a clean environment and verify that it
explains setup, DevEdu port 3000, tests, API use, Render deployment, and the assignment's
required AI-use disclosure. The student must review and complete that disclosure
accurately according to the assignment's wording.