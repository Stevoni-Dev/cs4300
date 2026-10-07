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

## Run locally

```sh
python manage.py migrate
python manage.py runserver 0.0.0.0:3000
```
