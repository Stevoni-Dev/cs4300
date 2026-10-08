# Movie Theater Booking

Django application for browsing movies, checking seat availability, registering and
signing in, booking seats, and reviewing private booking history. It provides Django
HTML pages and a REST API backed by the same database and booking service.

## Setup

Requires Python 3.12. From the `homework2` project root, create and activate the
virtual environment, then install the project and development dependencies:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Runtime dependencies are declared in `pyproject.toml`; the optional `dev` group adds
pytest and Pylint. Speckit and project commands should use `.venv/bin/python3.12`.

Create local settings from the example and replace its development secret:

```sh
cp .env.example .env
```

The root `.env` is loaded when present. Never commit or deploy `.env`; production
secrets and connection strings belong in the hosting provider's environment settings.
SQLite is used when `DATABASE_URL` is not supplied. `CSRF_TRUSTED_ORIGINS` can contain
comma-separated origins. With `DEBUG=True`, HTTPS origins under `*.lab.devedu.io` are
also trusted for DevEdu's HTTPS proxy; that development-only origin is not added when
`DEBUG=False`.

## Run locally and on DevEdu

```sh
.venv/bin/python3.12 manage.py migrate
.venv/bin/python3.12 manage.py runserver 0.0.0.0:3000
```

Open `http://localhost:3000/` locally, or open the forwarded port 3000 URL in DevEdu.
The root page lists movies. Register or sign in to book an available seat or manage the
movie catalog. Booking history is available to signed-in users from the shared
navigation. Migrations create the schema, not sample movie data; catalog and seat
inventory must be added through the API or provisioned for local testing.

## Tests

Run classified Django tests and Behave workflows from the project root:

```sh
.venv/bin/python3.12 -m pytest bookings/tests/unit -m unit
.venv/bin/python3.12 -m pytest bookings/tests/integration -m integration
.venv/bin/python3.12 manage.py behave --tags=integration
.venv/bin/python3.12 -m pylint .
```

The synchronized two-request booking test requires a PostgreSQL test database
configured through `DATABASE_URL`; an SQLite run skips that concurrency check.

## Pages and API

HTML routes:

| Route | Access | Purpose |
| --- | --- | --- |
| `/` or `/movies/` | Public | Browse movies |
| `/movies/<id>/` | Public | Movie details and seat availability |
| `/register/` | Public | Create an account |
| `/login/` | Public | Sign in |
| `/bookings/` | Signed in, POST | Book one available seat |
| `/bookings/history/` | Signed in | View private booking history |
| `/logout/` | Signed in, POST | End the session |

JSON API routes use `/api/`:

| Method and route | Access | Behavior |
| --- | --- | --- |
| `GET /api/movies/` | Public | List movies |
| `GET /api/movies/<id>/` | Public | Retrieve a movie |
| `POST /api/movies/` | Signed in | Create a movie |
| `PUT` or `PATCH /api/movies/<id>/` | Signed in | Replace or update a movie |
| `DELETE /api/movies/<id>/` | Signed in | Delete an unbooked movie; booking history yields `409` |
| `GET /api/seats/?movie=<id>` | Public | List a movie's seat availability |
| `GET /api/seats/<id>/` | Public | Retrieve a seat |
| `GET /api/bookings/` | Signed in | Own history, newest first, 20 per page (`?page=2`) |
| `POST /api/bookings/` | Signed in | Book one seat; a claimed seat yields `409` |

The DRF browsable API is available by opening these `/api/` routes in a browser.
Session-authenticated mutations require CSRF protection. Anonymous write requests use
DRF's configured authentication and permission responses.

## Render deployment

Live deployment: <https://movie-theater-booking-bwna.onrender.com/>

`render.yaml` defines a Render Blueprint with a Gunicorn web service and managed
PostgreSQL database. To deploy, create a new Blueprint in Render from this repository
and review the service and database plans before applying it. Render injects the
database connection through `DATABASE_URL`; the start command applies migrations
before launching Gunicorn. The build command installs the project and collects static
assets. WhiteNoise serves the collected static files. The Blueprint sets `DEBUG=False`,
generates `SECRET_KEY`, and configures Render host and CSRF origins. Never put production
credentials in the repository. Review the selected Render plans and database retention
terms before deploying.

## AI-use disclosure

This project used AI-assisted Spec-Driven Development following the workflow described
by [GitHub Spec Kit](https://github.github.io/spec-kit/). AI completed 100% of the code
implementation, test authoring, and debugging, and approximately 90% of the project
documentation.

Spec-Driven Development was introduced in class on September 24, 2026. The class book
describes the approach in its [chapter on AI across the software development
lifecycle](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#135-spec-driven-development).

My contribution was guiding and reviewing the development process. I established and
maintained the project constitution, specified requirements and acceptance criteria,
used checklists to assess completeness, and organized implementation through
dependency-aware tasks. I also directed the workflow, tested the application, and
provided feedback when behavior did not match the requirements. 
