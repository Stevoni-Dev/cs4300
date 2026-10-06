# Research: Movie Theater Booking

**Date**: 2026-10-06

## Decisions

### Django project and supported runtime

- **Decision**: Use Python 3.12 and Django 5.2 LTS, with the project package
  `movie_theater_booking` and the `bookings` app.
- **Rationale**: Python 3.12 is available in the coursework environment; Django 5.2 is
  an LTS release that supports it and provides server-rendered pages, authentication,
  migrations, and ORM-backed persistence in one framework.
- **Alternatives considered**: A separate frontend and API service would duplicate
  authentication and data access for a small assignment; another Python web framework
  would not satisfy the requested Django stack.

### DRF resource and authentication design

- **Decision**: Use DRF `ModelViewSet` with serializers for movie CRUD, a read-only seat
  availability viewset, and a create/list booking viewset. Use Django session
  authentication so browser templates and same-origin API calls share the signed-in
  user identity; keep movie/seat reads public and require authentication for writes and
  booking history/creation. Enforce CSRF for unsafe session-authenticated requests.
- **Rationale**: This aligns the specified collection URLs with DRF viewsets, avoids a
  second authentication mechanism, and permits the template and API experiences to
  share session and domain behavior.
- **Alternatives considered**: Token/JWT authentication adds credential lifecycle and
  storage concerns not required by this browser-focused phase. A separate API identity
  would conflict with the requirement that pages and API use the same data and users.

### Shared booking operation and duplicate prevention

- **Decision**: Route HTML and API booking submissions through one service wrapped in
  `transaction.atomic()`. Conditionally change a seat from available to reserved and
  create its booking in the same transaction. Add database uniqueness for
  `(movie, seat_number)` and one booking per seat; return a conflict response when the
  seat is already reserved. Validate that the requested seat belongs to the requested
  movie.
- **Rationale**: Application-level availability checks alone race under concurrent
  requests. Conditional writes, unique constraints, and atomic rollback enforce the
  at-most-one-booking rule at the persistence boundary. SQLite does not provide
  effective row-level `select_for_update()` locking, so correctness must not rely on it.
- **Alternatives considered**: A pre-check followed by an unconditional insert is
  vulnerable to two requests both observing an available seat. A distributed lock or
  switching databases exceeds the requested SQLite and assignment scope.

### SQLite on Render

- **Decision**: Read the SQLite database path from an environment variable, use a
  project-local database for development, and mount a Render persistent disk at
  `/var/data` for the deployed database. Deploy one web-service instance.
- **Rationale**: A Render service's ordinary filesystem is ephemeral; a SQLite file
  there can be lost on redeploy or restart. A persistent disk preserves the requested
  database across restarts, while a single instance avoids unsupported shared-file
  concurrency across replicas.
- **Alternatives considered**: PostgreSQL is a better multi-instance production
  database but conflicts with the explicit SQLite requirement. An ephemeral SQLite
  file is not acceptable for retaining booking history.
- **Operational constraint**: Confirm the course's Render account supports a persistent
  disk and the selected service plan before deployment. If not, the SQLite-on-Render
  requirement cannot provide durable production data without changing the storage
  requirement.

### Django templates, Bootstrap, and shared data

- **Decision**: Render movie listings, seat selection/booking, booking history,
  registration, and sign-in with Django templates and Bootstrap 5.3. Templates and DRF
  serializers read the same Django models; both booking entry points call the shared
  booking service.
- **Rationale**: Server rendering keeps the project small and avoids a frontend build
  system while satisfying the requested UI and shared-data behavior. Bootstrap supplies
  responsive layout primitives and accessible form/control conventions.
- **Alternatives considered**: A JavaScript SPA would add a separate client build and
  another data/authentication path without being requested.

### Test strategy and classification

- **Decision**: Use Django's test runner. Tag each test exactly `unit` or `integration`
  using Django test tags. Use unit tests for model rules, serializer validation, and
  booking service outcomes; use integration tests for DRF endpoints, Django pages,
  authentication, database persistence, and shared request workflows. Mark every
  Behave feature/scenario `@integration` and execute workflows through the Django test
  client.
- **Rationale**: Django's native tags map directly to the constitution's two exclusive
  classifications. Behave exercises cross-component user flows and therefore belongs
  to integration coverage.
- **Alternatives considered**: Duplicating the whole suite in a separate test runner
  would add configuration. Untagged tests would violate the constitution.
- **TDD rule**: For each behavior, write the smallest failing unit test first, observe
  the expected failure, implement the behavior, then add/update integration coverage
  for affected boundaries before refactoring.

### DevEdu and Render commands

- **Decision**: Run local development with Django's development server bound to
  `0.0.0.0:3000`; deploy with Gunicorn and collect static assets using WhiteNoise.
- **Rationale**: The requested DevEdu port is explicit. Render expects a production
  WSGI server and collected static assets rather than Django's development server.
- **Alternatives considered**: Running the development server in Render is not a
  production deployment pattern.

### Movie CRUD scope

- **Decision**: Include authenticated movie create, update, and delete operations in
  the phase-one API using the existing single user role; do not create a separate admin
  role or movie-management pages.
- **Rationale**: Movie catalog CRUD is a phase-one goal, not a later extension, and
  sharing the user role preserves the constitution's single-role rule.
- **Alternatives considered**: Omitting write operations would not satisfy CRUD.
- **Deletion rule**: Reject deletion of movies with booking history so reservations
  remain referentially valid and visible.

## Resolved Unknowns

No implementation technology unknowns remain. User credential fields and the exact
assignment-mandated AI disclosure wording are not specified; use Django's standard
username/password account flow and include an accurate, student-reviewed AI disclosure
section in the README without inventing assignment-specific wording.