---

description: "Dependency-ordered implementation tasks for Movie Theater Booking"
---

# Tasks: Movie Theater Booking

**Input**: Design documents from `specs/001-movie-theater-booking/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Testing**: TDD is mandatory. For each behavior, write tests first and observe the expected failure before implementation. Every Django test MUST be classified exactly once with `@tag("unit")` or `@tag("integration")`; Behave scenarios MUST be tagged `@integration`.

**Organization**: Tasks are grouped by the five independently reviewable user stories. Story dependencies are stated below.

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

- [x] T005 [P] Add integration tests in `bookings/tests/integration/test_auth_errors.py` using a test-only protected DRF view and URL fixture. Verify that anonymous requests follow DRF's default `SessionAuthentication` response (including status, absent `WWW-Authenticate` challenge, and default error body) and that authenticated invalid-CSRF requests are rejected; mark the module/class as integration and observe the expected failures. T050 later replaces this fixture with real protected endpoints.
- [x] T006 Remove project-specific authentication response handling from `movie_theater_booking/settings.py` and `bookings/api.py`; rely on DRF's default authentication classes and exception handler, while retaining `IsAuthenticated` for protected endpoints and explicit `AllowAny` on public reads.
- [x] T007 Configure `bookings/tests/` package structure and test classification conventions in `bookings/tests/__init__.py`, `bookings/tests/unit/`, and `bookings/tests/integration/`; ensure each Django test receives exactly one of the `unit` or `integration` tags.
- [x] T008 [P] Configure Behave-Django test discovery and test environment in `features/environment.py` and the project Behave configuration; ensure all feature/scenario tests use `@integration`.
- [x] T009 Configure shared Django messages, static asset handling, and base-template discovery in `movie_theater_booking/settings.py` for Bootstrap-backed server-rendered pages.

**Checkpoint**: Django starts, migrations can run, the test runner recognizes unit/integration classifications, and protected endpoints use DRF's standard authentication and permission behavior.

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
- [x] T015 [US1] Register `/api/movies/` and `/api/seats/` routes in `bookings/urls.py` and `movie_theater_booking/urls.py`, supporting movie list/detail and movie-scoped seat list/detail reads.
- [x] T016 [US1] Implement movie listing and seat availability views in `bookings/views.py` and templates in `bookings/templates/bookings/base.html`, `movie_list.html`, and `movie_detail.html`; use Bootstrap, label seat states accessibly, and render data from the same models used by the API.
- [x] T017 [US1] Run `bookings/tests/unit/test_movie_seat_models.py` with `.venv/bin/python -m pytest bookings/tests/unit/test_movie_seat_models.py -m unit` and the US1 integration tests in `bookings/tests/integration/test_movie_seat_api.py` and `bookings/tests/integration/test_browse_pages.py` with `.venv/bin/python -m pytest bookings/tests/integration/test_movie_seat_api.py bookings/tests/integration/test_browse_pages.py -m integration`; fix failures and confirm the movie/seat browse story passes independently.
- [x] T017a Resolve all C0114, C0115, C0116, C0301 pylint errors.
- [x] T017b Resolve all E0307, E1101, R0901.

**Checkpoint**: Visitors can browse listings and seat availability without authentication; API and pages show the same data.

---

## Phase 4: User Story 2 - Book an Available Seat (Priority: P1)

**Goal**: Register/sign in users and let signed-in users reserve one or more distinct available seats, without duplicate seat bookings.

**Independent Test**: Register and sign in; reserve a seat; confirm booking and reserved status; verify another reservation of that seat fails, two competing attempts yield at most one success, and a separate available seat can also be booked by the same user.

### Tests for User Story 2 (TDD - write and observe failures first)

- [x] T018 [P] [US2] Add unit tests in `bookings/tests/unit/test_registration_booking_service.py` for field validation, duplicate account identifier errors, failed registration creating no user, failed sign-in creating no authenticated session, atomic seat claim/booking, seat/movie relationship validation, one booking per seat, and multiple distinct seats per user/movie; mark `unit`.
- [x] T019 [P] [US2] Add API integration tests in `bookings/tests/integration/test_registration_booking_api.py` for registration/sign-in failures, DRF-native authentication/permission and CSRF responses, booking `201`, unauthenticated booking rejection according to configured DRF classes, unknown movie/seat `404`, mismatched movie/seat `400`, reserved-seat conflict `409`, and multiple distinct bookings; also use a transaction-backed test with a synchronized start and separate database connections to submit two requests for the same available seat against a PostgreSQL test database configured through `DATABASE_URL`, asserting exactly one `201`, one `409` whose response body says the seat is unavailable, and exactly one persisted booking. A SQLite-only run does not satisfy this concurrency test; mark `integration`.
- [x] T020 [P] [US2] Add HTML integration tests in `bookings/tests/integration/test_registration_booking_pages.py` for registration field/duplicate errors, generic invalid-sign-in feedback, seat booking confirmation, CSRF, and unavailable-seat messages; mark `integration`.
- [x] T021 [P] [US2] Add Behave scenarios in `features/booking.feature` and step definitions in `features/steps/booking_steps.py` for register/sign-in, browse, book, competing seat reservation, and a second distinct seat; tag every scenario `@integration`.

### Implementation for User Story 2

- [x] T022 [US2] Implement the Booking model and migration in `bookings/models.py` and `bookings/migrations/` with required Movie/Seat/User relations, server-set read-only `booking_date`, and a one-to-one Seat relation preventing more than one booking per seat.
- [x] T023 [US2] Implement registration and sign-in forms/views in `bookings/forms.py` and `bookings/views.py`; return field-specific errors for invalid/duplicate registration with no partial account, and the same generic sign-in failure for unknown account or wrong password.
- [x] T024 [US2] Implement the shared atomic booking operation in `bookings/services.py`; verify the seat belongs to the movie, conditionally claim only an `available` seat, create the booking for the authenticated user, and roll back both writes on failure.
- [x] T025 [US2] Implement booking serializer and create endpoint in `bookings/serializers.py` and `bookings/api.py`; ignore client-supplied user/date, enforce authentication/CSRF through DRF, preserve its standard authentication/permission responses, and map booking-domain failures to `400`, `404`, or `409` as specified.
- [x] T026 [US2] Implement seat booking form handling and registration/sign-in/booking templates in `bookings/views.py` and `bookings/templates/bookings/registration.html`, `login.html`, and `seat_booking.html`; call `bookings/services.py` so HTML and API share reservation rules.
- [x] T027 [US2] Run the US2 unit, API/page integration, and Behave tests; confirm the booking story passes independently after the US1 foundations.
- [x] T027a [US1] Make the movie listing the application home page by routing `/` to `movie_list_view` in `bookings/urls.py`; add an integration test in `bookings/tests/integration/test_browse_pages.py` and mark it `integration`.
- [x] T027b [US2] Add registration CSRF regression tests in `bookings/tests/integration/test_registration_booking_pages.py` and `features/booking.feature` with step definitions in `features/steps/booking_steps.py`; verify missing tokens are rejected and valid form tokens work with the DevEdu HTTPS `Origin`, and mark both as `integration`/`@integration`.
- [x] T027c [US2] Fix the DevEdu registration CSRF failure by trusting `https://*.lab.devedu.io` only when `DEBUG=True` in `movie_theater_booking/settings.py`; document the setting in `.env.example` and `README.md`, then rerun the T027b tests. Depends on T027b.


**Checkpoint**: A visitor can register/sign in and a signed-in user can book multiple distinct seats; any seat already reserved by any user can succeed only once.

---

## Phase 5: User Story 3 - Review Booking History (Priority: P2)

**Goal**: Show each signed-in user only their own bookings, newest first, in 20-item pages, with an informative empty state.

**Independent Test**: Seed bookings for two users; verify each only receives their own newest-first pages of at most 20, and a user with no bookings receives `count: 0`, `results: []`, and an HTML empty state.

### Tests for User Story 3 (TDD - write and observe failures first)

- [x] T028 [P] [US3] Add unit tests in `bookings/tests/unit/test_booking_history.py` for newest-first ordering and stable page boundaries at 20 items; mark `unit`.
- [x] T029 [P] [US3] Add API integration tests in `bookings/tests/integration/test_booking_history_api.py` for authenticated user scoping, page-number parameter, `count`/`next`/`previous`/`results`, page size 20, newest-first ordering, unauthenticated access rejection according to configured DRF classes, and empty `count: 0`, `results: []`; mark `integration`.
- [x] T030 [P] [US3] Add page integration tests in `bookings/tests/integration/test_booking_history_pages.py` for private user-scoped history, newest-first presentation, next-page navigation, and empty state; mark `integration`.
- [x] T031 [P] [US3] Add `@integration` Behave scenarios in `features/booking.feature` and `features/steps/booking_steps.py` for reviewing a user's bookings, excluding another user's data, pagination, and no-booking empty state.

### Implementation for User Story 3

- [x] T032 [US3] Implement a DRF page-number paginator with page size 20 and `booking_date` descending ordering in `bookings/api.py`; serialize only records owned by `request.user` with `count`, `next`, `previous`, and `results`.
- [x] T033 [US3] Implement the booking-history page in `bookings/views.py` and `bookings/templates/bookings/booking_history.html`, using the same user-scoped newest-first query and 20-item pagination as the API.
- [x] T034 [US3] Add booking-history navigation and empty-state presentation to `bookings/templates/bookings/base.html` and `booking_history.html` without exposing another user's data.
- [x] T035 [US3] Run US3 unit, integration, and Behave tests; confirm pagination and empty responses match `contracts/api.md`.

**Checkpoint**: Signed-in users can page through only their own newest-first history; empty API/page results are explicit.

---

## Phase 6: User Story 4 - Maintain the Movie Catalog (Priority: P2)

**Goal**: Allow any signed-in user in the single user role to create, retrieve, update, and delete movies through the API; preserve movies with booking history.

**Independent Test**: Through the API, create a movie, retrieve and update it, delete it before bookings exist, reject deletion after booking history exists, reject anonymous writes, and confirm listing pages reflect changes.

### Tests for User Story 4 (TDD - write and observe failures first)

- [x] T036 [P] [US4] Add unit tests in `bookings/tests/unit/test_movie_crud.py` for required fields, positive duration/date validation, partial update validation, and delete protection when bookings exist; mark `unit`.
- [x] T037 [P] [US4] Add API integration tests in `bookings/tests/integration/test_movie_crud_api.py` for list/retrieve/create/update/partial-update/delete, anonymous write rejection according to configured DRF classes, invalid-field `400`, missing-resource `404`, delete-with-bookings `409`, and public listing consistency; mark `integration`.
- [x] T038 [P] [US4] Add `@integration` Behave scenarios in `features/booking.feature` and `features/steps/booking_steps.py` for signed-in catalog creation/update/deletion, preservation after bookings, and anonymous write rejection.

### Implementation for User Story 4

- [x] T039 [US4] Extend `MovieSerializer` in `bookings/serializers.py` with create/update validation for required non-empty bounded title, required description/date, and positive whole-minute duration.
- [x] T040 [US4] Enable authenticated movie create/update/delete actions in the DRF movie viewset in `bookings/api.py` while keeping movie list/detail reads public and using the single signed-in user role for every write.
- [x] T041 [US4] Reject deletion of any movie with booking history in `bookings/api.py` or `bookings/services.py` using the documented `409` response; allow deletion only when no booking history exists.
- [x] T042 [US4] Run US4 unit, API integration, and Behave tests; confirm movie CRUD changes appear in the existing listing page without a separate management role or page.

**Checkpoint**: Movie catalog CRUD is fully available to the single signed-in user role and cannot erase booking history.

---

## Phase 6a: User Story 5 - Maintain a Movie's Seat Inventory (Priority: P2)

**Goal**: Allow any signed-in user in the single user role to create, retrieve, update, and delete seats at `/api/seats/` (spec FR-017 to FR-020); the `GET /api/seats/?movie=` list behavior and public reads are unchanged, and no movie-nested seat routes are added.

**Independent Test**: Through the API, create seats for a movie, retrieve and rename one, reject a duplicate number within the movie (while allowing it in another movie), delete an unbooked seat, reject deletion of a booked seat with `409`, reject anonymous writes, and confirm the movie detail page and `GET /api/seats/?movie=<id>` reflect each change.

### Tests for User Story 5 (TDD - write and observe failures first)

- [ ] T051 [P] [US5] Add unit tests in `bookings/tests/unit/test_seat_crud.py` for seat serializer validation (FR-018: required, blank/whitespace-only, over-length, and non-string `seat_number`; duplicate within a movie rejected with a field error; same number allowed in a different movie; a rename to the seat's own current number is valid), server-controlled fields (FR-019: new seats are `available`; client `status` is ignored; `movie` is required on create and ignored on update), and seat deletion protection when a booking exists (FR-020); mark `unit`.
- [ ] T052 [P] [US5] Add API integration tests in `bookings/tests/integration/test_seat_crud_api.py` for `/api/seats/` list/retrieve/create/update/partial-update/delete: `201` with `status: available` even when the client sends `reserved`; missing/malformed `movie` on create `400`; unknown `movie` on create `404`; `movie` in an update body ignored so the seat stays with its movie; duplicate/invalid number `400` with a field-specific error; unknown seat `404` on retrieve/update/delete; anonymous writes rejected according to configured DRF classes with the inventory unchanged while anonymous reads succeed; authenticated invalid-CSRF writes rejected with no mutation; delete of a booked seat `409` with the seat and booking intact; deleting an unbooked movie removes its seats; created/renamed/deleted seats appear in `GET /api/seats/?movie=<id>` and the movie detail page; mark `integration`.
- [ ] T053 [P] [US5] Add `@integration` Behave scenarios in `features/booking.feature` and `features/steps/booking_steps.py` for a signed-in user adding seats to a movie and then another user booking one, rejecting a duplicate seat number, rejecting deletion of a booked seat, and rejecting anonymous seat creation.
- [ ] T052a [P] [US5] Before changing `SeatViewSet`, run `bookings/tests/integration/test_movie_seat_api.py` (T011) and record that it passes; it must pass again unchanged after T055 to prove the public `GET /api/seats/` list (required `movie`, `400`/`404`, empty result) and `GET /api/seats/{id}/` behavior did not regress. Add to `bookings/tests/integration/test_seat_crud_api.py` a PostgreSQL-backed test for the delete-versus-booking race: a booking committed after the delete's protected-relation check but before the row delete must produce `409` (not a `500` from a foreign-key `IntegrityError`) and leave the seat and booking intact; mark `integration`.

### Implementation for User Story 5

- [ ] T054 [US5] Add seat write validation in `bookings/serializers.py`: trimmed, required, non-blank `seat_number` bounded by the model field; read-only `status`; `movie` required and writable only on create (read-only on update); a `validate` check that rejects duplicates of `seat_number` within the seat's movie (excluding the instance being updated) with a field-specific error, because DRF will not auto-apply the model `UniqueConstraint` when `movie` is not a normal writable field on update. Use `NotFoundPrimaryKeyRelatedField` for `movie` so an unknown movie returns `404`. Keep the existing read output (`id`, `movie`, `seat_number`, `status`) unchanged.
- [ ] T055 [US5] Convert `SeatViewSet` in `bookings/api.py` from read-only to a `ModelViewSet` at the existing `/api/seats/` route: keep the required `?movie=` list behavior (`400`/`404`) and `AllowAny` for `list`/`retrieve`, use `IsAuthenticated` for create/update/delete, set `available` status on create, and map both `ProtectedError` and a database `IntegrityError` raised by a concurrent booking in `perform_destroy` to a `409` conflict exception (as `MovieViewSet` does for `ProtectedError`). Update its docstring that says seats are provisioned separately.
- [ ] T056 [US5] Confirm `bookings/urls.py` needs no new routes (the existing `router.register(r"seats", SeatViewSet, ...)` now serves all actions), add no movie-nested seat routes, and add a test asserting `/api/movies/{id}/seats/` returns `404`.
- [ ] T056a [P] [US5] Correct documentation made stale by the writable seat endpoint (completes the intent of T043): the `bookings/api.py` module docstring ("movie mutations require authentication" must also cover seat mutations), the `SeatViewSet` class docstring, and the `SeatSerializer` docstring in `bookings/serializers.py` (now validates writes); document the `/api/seats/` write rules in the module docstring.
- [ ] T057 [US5] Update `contracts/api.md` (replace the "provisioned separately" note under Seats and document the new endpoints, status codes `201`/`200`/`204`/`400`/`404`/`409`, and server-controlled fields), `data-model.md` (Seat create/delete rules and the remaining `available -> reserved` transition), `plan.md`, `quickstart.md` (seed seats through the API), and `README.md` (API routes table and the sentence that says seats are added through the API).
- [ ] T058 [US5] Run the US5 unit, API integration, and Behave tests, then the full suite and `.venv/bin/python3.12 -m pylint .`; confirm US1 to US4 tests still pass, no migration is required, and the new endpoints satisfy FR-017 to FR-020.

**Checkpoint**: A movie can be made bookable using only the API; seat inventory changes never alter or erase booking history.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, deployment readiness, accessibility, and cross-story validation.

- [x] T043 [P] Document public models, serializers, viewsets, booking service, and page handlers in `bookings/models.py`, `bookings/serializers.py`, `bookings/api.py`, `bookings/services.py`, and `bookings/views.py`; update `README.md` with setup, DevEdu port 3000, tests, API routes, Render deployment, and an accurate assignment-required AI-use disclosure.
- [x] T044 [P] Add Render deployment configuration in `render.yaml` for Gunicorn, static collection, startup migrations, environment settings, and a managed PostgreSQL database connected through `DATABASE_URL`; do not configure a persistent SQLite disk.
- [x] T045 [P] Review Bootstrap templates in `bookings/templates/bookings/` against keyboard access, visible focus, clear status/error feedback, responsive supported viewports, and common base navigation; fix requirement gaps.
- [x] T050 After T042, remove T005's test-only view/URL fixture from `bookings/tests/integration/test_auth_errors.py`. Reuse existing integration coverage for anonymous booking/history/movie-write rejection and invalid-CSRF booking requests; do not duplicate those cases. Add real-route integration coverage for authenticated invalid-CSRF movie create/update/delete requests, verifying rejection and no catalog mutation without pinning a project-wide status or response body. Complete this before T046.
- [x] T046 Run the Django unit, integration, and Behave test suites; confirm the project passes its final validation set without regressions.
- [x] T047 Follow `specs/001-movie-theater-booking/quickstart.md` from a clean DevEdu environment, including migrations and `python manage.py runserver 0.0.0.0:3000`; update `README.md` if any setup or expected result differs.
- [x] T048 Validate Render cold-start readiness using `render.yaml`; verify the app is ready within the configured startup/readiness window, create a booking, restart the app service, and confirm the booking remains in the user's history through PostgreSQL.
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
- **US5 (P2)**: Depends on US1 Seat model and read routes, US2 Booking model (delete protection), and US4 movie-API patterns; T058 must pass before T046 is re-run for final validation.

### Within Each User Story

- Write unit, API/page integration, and Behave tests first; run them and observe expected failures before implementation.
- Implement models and migrations before services, serializers/viewsets, and templates that depend on them.
- Run the story's classified tests at its checkpoint before starting dependent stories.

### Parallel Opportunities

- During US1 test-first work: T010, T011, and T012 can be written in parallel because they touch separate test files.
- During US2 test-first work: T018–T021 can be prepared in parallel across unit, API, page, and Behave files.
- During US3 test-first work: T028–T031 can be prepared in parallel across unit, API, page, and Behave files.
- During US4 test-first work: T036–T038 can be prepared in parallel.
- During US5 test-first work: T051–T053 can be prepared in parallel across unit, API, and Behave files; T054–T056 touch `serializers.py`, `api.py`, and `urls.py` and may be parallelized only after their tests are observed failing.
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
4. Add US3 booking history, US4 movie catalog CRUD, and US5 seat inventory CRUD as separate increments.
5. Complete cross-cutting documentation, test-suite, UI, and Render checks.

### Incremental Delivery

- Deliver US1 with its unit/integration tests, then confirm the public browse flow works.
- Deliver US2 after US1, with TDD evidence and API/HTML/Behave booking coverage.
- Deliver US3, US4, and US5 independently after their declared model/auth prerequisites.
- Keep the application releasable at each story checkpoint; do not start a dependent story before its prerequisite checkpoint passes.

---

## Notes

- Every task uses the required checkbox + sequential ID format and names concrete project paths.
- `[P]` marks only work in separate files with satisfied dependencies.
- `[US#]` labels map to the five user stories in `spec.md`.
- Every behavior task has test-first tasks; observe the expected red result before implementation.
- All test tasks preserve the constitution's mutually exclusive `unit`/`integration` taxonomy; Behave is always `integration`.
