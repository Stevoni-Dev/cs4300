---

description: "Dependency-ordered implementation tasks for Movie Theater Booking"
---

# Tasks: Movie Theater Booking

**Input**: Design documents from `specs/001-movie-theater-booking/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Testing**: TDD is mandatory. For each behavior, write tests first and observe the expected failure before implementation. Every Django test MUST be classified exactly once with `@tag("unit")` or `@tag("integration")`; Behave scenarios MUST be tagged `@integration`.

**Organization**: Tasks are grouped by the four independently reviewable user stories. Story dependencies are stated below.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel with other tasks in the phase because files differ and prerequisites are complete.
- **[Story]**: User story label mapped to `spec.md`.
- Each task names the relevant project paths.

## Phase 1: Setup

**Purpose**: Create the Django project and reproducible local environment.

- [x] T001 Create Django project package `movie_theater_booking/` and root `manage.py` per `plan.md`.
- [x] T002 Create root `pyproject.toml` with project metadata and the required runtime packages: Django, Django REST Framework, Behave-Django, Bootstrap/static support, Gunicorn, WhiteNoise, `dj-database-url`, and Psycopg; do not create or rely on `requirements.txt`.
- [x] T002a Add Pylint as an optional `dev` dependency in `pyproject.toml` (installable with `.[dev]`) and configure Pylint there to ignore `.venv`, other virtual environments, generated build/package output, collected static files, and Django migration directories.
- [x] T002b Create a root `README.md` with minimum essential project setup and run information, including that `.venv` will be leveraged to provide Pylint and other package-dependent capabilities to the Speckit agent.
- [x] T003 Add environment-variable examples for `SECRET_KEY`, `DEBUG`, allowed hosts, trusted CSRF origins, local SQLite path, and the Render `DATABASE_URL` setting in `.env.example` without including credentials.
- [x] T004 Configure `movie_theater_booking/settings.py` for the `bookings` app, Django auth, DRF, templates, static assets, local SQLite and PostgreSQL settings parsed from `DATABASE_URL` with `dj-database-url`; add root URL and WSGI/ASGI wiring in `movie_theater_booking/urls.py`, `movie_theater_booking/wsgi.py`, and `movie_theater_booking/asgi.py`.
- [x] T004a Run `.venv/bin/python3.12 -m pylint .`, resolve all reported Pylint errors and findings in project Python code, and confirm the score exceeds the configured 8.0 minimum.

---

## Phase 2: Foundational

**Purpose**: Establish shared auth/error behavior and test harnesses required before user stories.

- [x] T005 [P] Write initial integration tests in `bookings/tests/integration/test_auth_errors.py` using a test-only protected DRF view and URL fixture, not a production route, to verify anonymous `401` responses use the agreed JSON error shape and authenticated invalid-CSRF requests return `403`; mark the module/class `@tag("integration")` and observe the expected failures. T050 later replaces this fixture with the real protected endpoints.
- [x] T006 Implement shared DRF authentication failure handling in `movie_theater_booking/settings.py` and `bookings/api.py` so anonymous protected requests return the agreed `401` shape while authenticated forbidden/CSRF requests remain `403`.
- [x] T007 Configure `bookings/tests/` package structure and test classification conventions in `bookings/tests/__init__.py`, `bookings/tests/unit/`, and `bookings/tests/integration/`; ensure each Django test receives exactly one of the `unit` or `integration` tags.
- [x] T008 [P] Configure Behave-Django test discovery and test environment in `features/environment.py` and the project Behave configuration; ensure all feature/scenario tests use `@integration`.
- [x] T009 Configure shared Django messages, static asset handling, and base-template discovery in `movie_theater_booking/settings.py` for Bootstrap-backed server-rendered pages.

**Checkpoint**: Django starts, migrations can run, the test runner recognizes unit/integration classifications, and the shared API auth policy is covered.

---

## Phase 3: User Story 1 - Browse Movies and Seat Availability (Priority: P1)

**Goal**: Let visitors browse movie details and see movie-scoped seat status.

**Independent Test**: With movies and seat inventory supplied, verify listing/detail data and available/reserved seat states through both the API and pages; verify empty movie listings.

### Tests for User Story 1 (TDD - write and observe failures first)

- [x] T010 [P] [US1] Add unit tests in `bookings/tests/unit/test_movie_seat_models.py` for Movie required title/description/date, positive duration, Seat status values, and uniqueness of `(movie, seat_number)`; mark `unit`.
- [x] T011 [P] [US1] Add API integration tests in `bookings/tests/integration/test_movie_seat_api.py` for public movie list/detail and `GET /api/seats/?movie=<id>`, including missing/invalid movie `400`, unknown movie `404`, and empty results; mark `integration`.
- [x] T012 [P] [US1] Add page integration tests in `bookings/tests/integration/test_browse_pages.py` for movie listing, movie detail/seat availability, empty states, and shared API/template database data; mark `integration`.

### Implementation for User Story 1

- [x] T013 [US1] Implement Movie and Seat models in `bookings/models.py` with Movie `title` required/non-empty/bounded, `description` required, `release_date` required date, `duration` required positive integer, Seat `seat_number` required and unique within its movie, and status limited to `available` or `reserved`; create `bookings/migrations/` migration.
- [x] T014 [US1] Add read serializers and public read-only movie/seat viewsets in `bookings/serializers.py` and `bookings/api.py`; require `movie` on seat-list requests and return the specified `400`/`404` outcomes.
- [ ] T015 [US1] Register `/api/movies/` and `/api/seats/` routes in `bookings/urls.py` and `movie_theater_booking/urls.py`, supporting movie list/detail and movie-scoped seat list/detail reads.
- [ ] T016 [US1] Implement movie listing and seat availability views in `bookings/views.py` and templates in `bookings/templates/bookings/base.html`, `movie_list.html`, and `seat_booking.html`; use Bootstrap, label seat states accessibly, and render data from the same models used by the API.
- [ ] T017 [US1] Run `python manage.py test --tag=unit` and the US1 integration tests; fix failures and confirm the movie/seat browse story passes independently.

**Checkpoint**: Visitors can browse listings and seat availability without authentication; API and pages show the same data.

---

## Phase 4: User Story 2 - Book an Available Seat (Priority: P1)

**Goal**: Register/sign in users and let signed-in users reserve one or more distinct available seats, without duplicate seat bookings.

**Independent Test**: Register and sign in; reserve a seat; confirm booking and reserved status; verify another reservation of that seat fails, two competing attempts yield at most one success, and a separate available seat can also be booked by the same user.

### Tests for User Story 2 (TDD - write and observe failures first)

- [ ] T018 [P] [US2] Add unit tests in `bookings/tests/unit/test_registration_booking_service.py` for field validation, duplicate account identifier errors, failed registration creating no user, failed sign-in creating no authenticated session, atomic seat claim/booking, seat/movie relationship validation, one booking per seat, and multiple distinct seats per user/movie; mark `unit`.
- [ ] T019 [P] [US2] Add API integration tests in `bookings/tests/integration/test_registration_booking_api.py` for registration/sign-in failures, shared `401`/`403` behavior, booking `201`, anonymous `401`, unknown movie/seat `404`, mismatched movie/seat `400`, reserved-seat conflict `409`, and multiple distinct bookings; also use a transaction-backed test with a synchronized start and separate database connections to submit two requests for the same available seat against a PostgreSQL test database configured through `DATABASE_URL`, asserting exactly one `201`, one `409` whose response body says the seat is unavailable, and exactly one persisted booking. A SQLite-only run does not satisfy this concurrency test; mark `integration`.
- [ ] T020 [P] [US2] Add HTML integration tests in `bookings/tests/integration/test_registration_booking_pages.py` for registration field/duplicate errors, generic invalid-sign-in feedback, seat booking confirmation, CSRF, and unavailable-seat messages; mark `integration`.
- [ ] T021 [P] [US2] Add Behave scenarios in `features/booking.feature` and step definitions in `features/steps/booking_steps.py` for register/sign-in, browse, book, competing seat reservation, and a second distinct seat; tag every scenario `@integration`.

### Implementation for User Story 2

- [ ] T022 [US2] Implement the Booking model and migration in `bookings/models.py` and `bookings/migrations/` with required Movie/Seat/User relations, server-set read-only `booking_date`, and a one-to-one Seat relation preventing more than one booking per seat.
- [ ] T023 [US2] Implement registration and sign-in forms/views in `bookings/forms.py` and `bookings/views.py`; return field-specific errors for invalid/duplicate registration with no partial account, and the same generic sign-in failure for unknown account or wrong password.
- [ ] T024 [US2] Implement the shared atomic booking operation in `bookings/services.py`; verify the seat belongs to the movie, conditionally claim only an `available` seat, create the booking for the authenticated user, and roll back both writes on failure.
- [ ] T025 [US2] Implement booking serializer and create endpoint in `bookings/serializers.py` and `bookings/api.py`; ignore client-supplied user/date, enforce authentication/CSRF, and map failures to `401`, `400`, `403`, `404`, or `409` as specified.
- [ ] T026 [US2] Implement seat booking form handling and registration/sign-in/booking templates in `bookings/views.py` and `bookings/templates/bookings/registration.html`, `login.html`, and `seat_booking.html`; call `bookings/services.py` so HTML and API share reservation rules.
- [ ] T027 [US2] Run the US2 unit, API/page integration, and Behave tests; confirm the booking story passes independently after the US1 foundations.

**Checkpoint**: A visitor can register/sign in and a signed-in user can book multiple distinct seats; any seat already reserved by any user can succeed only once.

---

## Phase 5: User Story 3 - Review Booking History (Priority: P2)

**Goal**: Show each signed-in user only their own bookings, newest first, in 20-item pages, with an informative empty state.

**Independent Test**: Seed bookings for two users; verify each only receives their own newest-first pages of at most 20, and a user with no bookings receives `count: 0`, `results: []`, and an HTML empty state.

### Tests for User Story 3 (TDD - write and observe failures first)

- [ ] T028 [P] [US3] Add unit tests in `bookings/tests/unit/test_booking_history.py` for newest-first ordering and stable page boundaries at 20 items; mark `unit`.
- [ ] T029 [P] [US3] Add API integration tests in `bookings/tests/integration/test_booking_history_api.py` for authenticated user scoping, page-number parameter, `count`/`next`/`previous`/`results`, page size 20, newest-first ordering, anonymous `401`, and empty `count: 0`, `results: []`; mark `integration`.
- [ ] T030 [P] [US3] Add page integration tests in `bookings/tests/integration/test_booking_history_pages.py` for private user-scoped history, newest-first presentation, next-page navigation, and empty state; mark `integration`.
- [ ] T031 [P] [US3] Add `@integration` Behave scenarios in `features/booking.feature` and `features/steps/booking_steps.py` for reviewing a user's bookings, excluding another user's data, pagination, and no-booking empty state.

### Implementation for User Story 3

- [ ] T032 [US3] Implement a DRF page-number paginator with page size 20 and `booking_date` descending ordering in `bookings/api.py`; serialize only records owned by `request.user` with `count`, `next`, `previous`, and `results`.
- [ ] T033 [US3] Implement the booking-history page in `bookings/views.py` and `bookings/templates/bookings/booking_history.html`, using the same user-scoped newest-first query and 20-item pagination as the API.
- [ ] T034 [US3] Add booking-history navigation and empty-state presentation to `bookings/templates/bookings/base.html` and `booking_history.html` without exposing another user's data.
- [ ] T035 [US3] Run US3 unit, integration, and Behave tests; confirm pagination and empty responses match `contracts/api.md`.

**Checkpoint**: Signed-in users can page through only their own newest-first history; empty API/page results are explicit.

---

## Phase 6: User Story 4 - Maintain the Movie Catalog (Priority: P2)

**Goal**: Allow any signed-in user in the single user role to create, retrieve, update, and delete movies through the API; preserve movies with booking history.

**Independent Test**: Through the API, create a movie, retrieve and update it, delete it before bookings exist, reject deletion after booking history exists, reject anonymous writes, and confirm listing pages reflect changes.

### Tests for User Story 4 (TDD - write and observe failures first)

- [ ] T036 [P] [US4] Add unit tests in `bookings/tests/unit/test_movie_crud.py` for required fields, positive duration/date validation, partial update validation, and delete protection when bookings exist; mark `unit`.
- [ ] T037 [P] [US4] Add API integration tests in `bookings/tests/integration/test_movie_crud_api.py` for list/retrieve/create/update/partial-update/delete, anonymous `401`, invalid-field `400`, missing-resource `404`, delete-with-bookings `409`, and public listing consistency; mark `integration`.
- [ ] T038 [P] [US4] Add `@integration` Behave scenarios in `features/booking.feature` and `features/steps/booking_steps.py` for signed-in catalog creation/update/deletion, preservation after bookings, and anonymous write rejection.

### Implementation for User Story 4

- [ ] T039 [US4] Extend `MovieSerializer` in `bookings/serializers.py` with create/update validation for required non-empty bounded title, required description/date, and positive whole-minute duration.
- [ ] T040 [US4] Enable authenticated movie create/update/delete actions in the DRF movie viewset in `bookings/api.py` while keeping movie list/detail reads public and using the single signed-in user role for every write.
- [ ] T041 [US4] Reject deletion of any movie with booking history in `bookings/api.py` or `bookings/services.py` using the documented `409` response; allow deletion only when no booking history exists.
- [ ] T042 [US4] Run US4 unit, API integration, and Behave tests; confirm movie CRUD changes appear in the existing listing page without a separate management role or page.

**Checkpoint**: Movie catalog CRUD is fully available to the single signed-in user role and cannot erase booking history.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, deployment readiness, accessibility, and cross-story validation.

- [ ] T043 [P] Document public models, serializers, viewsets, booking service, and page handlers in `bookings/models.py`, `bookings/serializers.py`, `bookings/api.py`, `bookings/services.py`, and `bookings/views.py`; update `README.md` with setup, DevEdu port 3000, tests, API routes, Render deployment, and an accurate assignment-required AI-use disclosure.
- [ ] T044 [P] Add Render deployment configuration in `render.yaml` for Gunicorn, static collection, startup migrations, environment settings, and a managed PostgreSQL database connected through `DATABASE_URL`; do not configure a persistent SQLite disk.
- [ ] T045 [P] Review Bootstrap templates in `bookings/templates/bookings/` against keyboard access, visible focus, clear status/error feedback, responsive supported viewports, and common base navigation; fix requirement gaps.
- [ ] T050 After T042, refactor the auth-error integration tests in `bookings/tests/integration/test_auth_errors.py` to remove T005's test-only view/URL fixture and exercise the real protected routes: anonymous booking creation and booking-history requests, plus anonymous movie create/update/delete requests, must return `401` with the same JSON error shape; authenticated invalid-CSRF booking and movie-write requests must return `403`. Complete this before T046.
- [ ] T046 Run the Django unit, integration, and Behave test suites; confirm the project passes its final validation set without regressions.
- [ ] T047 Follow `specs/001-movie-theater-booking/quickstart.md` from a clean DevEdu environment, including migrations and `python manage.py runserver 0.0.0.0:3000`; update `README.md` if any setup or expected result differs.
- [ ] T048 Validate Render cold-start readiness using `render.yaml`; verify the app is ready within the configured startup/readiness window, create a booking, restart the app service, and confirm the booking remains in the user's history through PostgreSQL.
- [ ] T049 Run the SC-004 usability evaluation after T045: prepare a movie with an available seat and a test account, ask one first-time participant to book an available seat without hints, and record independent completion of browsing, seat identification, and booking plus any observed blockers; pass when all three steps are completed independently.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; establishes the Django project and settings.
- **Foundational (Phase 2)**: Depends on Setup; blocks every user story.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 7)**: Depends on all desired stories; deployment/docs review can be prepared in parallel with final story work, but acceptance runs after all selected stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; provides public Movie/Seat read models and browse routes.
- **US2 (P1)**: Depends on US1 seat/movie models and availability routes; adds user registration/sign-in and Booking.
- **US3 (P2)**: Depends on US2 Booking and authentication; tests independently with bookings for multiple users.
- **US4 (P2)**: Depends on US1 Movie model/API and US2 Booking model to preserve history during deletion.

### Within Each User Story

- Write unit, API/page integration, and Behave tests first; run them and observe expected failures before implementation.
- Implement models and migrations before services, serializers/viewsets, and templates that depend on them.
- Run the story's classified tests at its checkpoint before starting dependent stories.

### Parallel Opportunities

- During US1 test-first work: T010, T011, and T012 can be written in parallel because they touch separate test files.
- During US2 test-first work: T018–T021 can be prepared in parallel across unit, API, page, and Behave files.
- During US3 test-first work: T028–T031 can be prepared in parallel across unit, API, page, and Behave files.
- During US4 test-first work: T036–T038 can be prepared in parallel.
- After test tasks are complete, independent serializer/view/template tasks may be parallelized only when different files are owned and no prerequisite is incomplete.
- T043–T045 touch separate docs/deployment/template review paths and may proceed in parallel after their relevant stories stabilize.

---

## Parallel Example: User Story 2

```text
Task: T018 unit tests for registration and booking service in bookings/tests/unit/test_registration_booking_service.py
Task: T019 API integration tests in bookings/tests/integration/test_registration_booking_api.py
Task: T020 page integration tests in bookings/tests/integration/test_registration_booking_pages.py
Task: T021 Behave integration scenarios in features/booking.feature and features/steps/booking_steps.py

After those tests are observed failing, implement the related behavior in bookings/forms.py, bookings/models.py, bookings/services.py, bookings/serializers.py, bookings/api.py, and bookings/views.py.
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 browse movies and seat availability as the first demonstrable slice.
3. Complete US2 registration/sign-in and atomic seat booking next; this is the first end-to-end booking MVP.
4. Add US3 booking history and US4 movie catalog CRUD as separate increments.
5. Complete cross-cutting documentation, test-suite, UI, and Render checks.

### Incremental Delivery

- Deliver US1 with its unit/integration tests, then confirm the public browse flow works.
- Deliver US2 after US1, with TDD evidence and API/HTML/Behave booking coverage.
- Deliver US3 and US4 independently after their declared model/auth prerequisites.
- Keep the application releasable at each story checkpoint; do not start a dependent story before its prerequisite checkpoint passes.

---

## Notes

- Every task uses the required checkbox + sequential ID format and names concrete project paths.
- `[P]` marks only work in separate files with satisfied dependencies.
- `[US#]` labels map to the four user stories in `spec.md`.
- Every behavior task has test-first tasks; observe the expected red result before implementation.
- All test tasks preserve the constitution's mutually exclusive `unit`/`integration` taxonomy; Behave is always `integration`.
