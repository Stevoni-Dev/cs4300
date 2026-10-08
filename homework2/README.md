# Movie Theater Booking

Django application for browsing movies, checking seat availability, making bookings, and reviewing booking history.

## Setup

Requires Python 3.12. Create and activate the project virtual environment, then install the application and development tools:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The `.venv` environment is leveraged by the Speckit agent to provide Pylint and other package-dependent capabilities. The optional `dev` dependency installs Pylint; runtime packages are declared in `pyproject.toml`.

For local settings, copy `.env.example` to `.env` and replace the development secret:

```sh
cp .env.example .env
```

Never track or commit `.env`, and never push or deploy it to production. The root `.env`
file is loaded only when present; production settings must be configured through the
hosting provider's environment variables. Render supplies its PostgreSQL `DATABASE_URL`.
In debug mode, the application also trusts HTTPS origins under `*.lab.devedu.io` so
registration and booking forms work through DevEdu's HTTPS proxy. This development-only
origin is not added when `DEBUG=False`.

## Run locally

```sh
python manage.py migrate
python manage.py runserver 0.0.0.0:3000
```
