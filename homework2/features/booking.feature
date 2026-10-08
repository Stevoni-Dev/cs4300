@integration
Feature: Reserve movie seats
  Visitors can register and sign in before booking available seats.

  @integration
  Scenario: Register, browse, and book an available seat
    Given movie "Arrival" has available seats "A1" and "A2"
    And the visitor opens the registration page
    When the visitor registers with username "new-booker" and password "valid-password-123"
    Then account "new-booker" exists
    When the visitor signs in with username "new-booker" and password "valid-password-123"
    Then the visitor is signed in
    When the visitor browses movie "Arrival"
    Then the page shows available seats "A1" and "A2"
    When the signed-in visitor books seat "A1"
    Then the booking is confirmed for seat "A1"

  @integration
  Scenario: Registration succeeds with a valid CSRF token
    Given the visitor opens registration with CSRF checks enabled
    When the visitor submits valid CSRF-protected registration data for "csrf-behave-user"
    Then account "csrf-behave-user" exists

  @integration
  Scenario: A second user cannot book an occupied seat
    Given movie "Arrival" has available seats "A1" and "A2"
    And accounts "first-booker" and "second-booker" exist
    When account "first-booker" books seat "A1"
    And account "second-booker" tries to book seat "A1"
    Then the first booking succeeds and the second sees an unavailable-seat message

  @integration
  Scenario: One user can book two distinct seats
    Given movie "Arrival" has available seats "A1" and "A2"
    And account "multi-booker" exists and is signed in
    When the signed-in visitor books seats "A1" and "A2"
    Then both distinct bookings are confirmed

  @integration
  Scenario: Review private booking history across pages
    Given signed-in account "history-reader" has 21 bookings and another user's booking
    When the account opens booking history
    Then page one shows the 20 newest bookings without the other user's booking
    When the account opens the next booking history page
    Then page two shows the remaining booking without a next page

  @integration
  Scenario: An account with no bookings sees an empty history
    Given signed-in account "empty-history-reader" has no bookings
    When the account opens booking history
    Then the history page shows the empty state

  @integration
  Scenario: A signed-in user manages the movie catalog
    Given signed-in account "catalog-manager" can manage movies
    When the catalog manager creates movie "Catalog Feature"
    Then the movie is created successfully
    When the catalog manager updates the movie title to "Catalog Feature Revised"
    Then the movie update is visible in the public catalog
    When the catalog manager deletes the movie
    Then the movie is no longer in the catalog

  @integration
  Scenario: A movie with booking history cannot be deleted
    Given signed-in account "catalog-protector" has a movie with booking history
    When the catalog manager deletes that movie
    Then deletion is rejected and the booking history is preserved

  @integration
  Scenario: Anonymous visitors cannot write to the movie catalog
    Given movie "Protected Catalog Movie" exists
    When an anonymous visitor attempts movie create update and delete requests
    Then all anonymous movie writes are rejected and the movie remains unchanged

  @integration
  Scenario: A signed-in user adds a seat another user can book
    Given movie "Seat Inventory Feature" has available seats "A1" and "A2"
    And signed-in account "seat-manager" can manage seats
    When the seat manager adds seat "A3"
    And another account books seat "A3"
    Then seat "A3" is added and can be booked by the other account

  @integration
  Scenario: A user cannot add a duplicate seat number
    Given movie "Duplicate Seat Feature" has available seats "A1" and "A2"
    And signed-in account "duplicate-seat-manager" can manage seats
    When the seat manager adds seat "A3"
    And the seat manager tries to add duplicate seat "A3"
    Then the duplicate seat number is rejected

  @integration
  Scenario: A booked seat cannot be deleted
    Given movie "Booked Seat Feature" has available seats "A1" and "A2"
    And signed-in account "booked-seat-manager" can manage seats
    When the seat manager adds seat "A3"
    And another account books seat "A3"
    And the seat manager deletes seat "A3"
    Then the booked seat deletion is rejected

  @integration
  Scenario: Anonymous visitors cannot add seats
    Given movie "Anonymous Seat Feature" has available seats "A1" and "A2"
    When an anonymous visitor attempts to add seat "ANON"
    Then anonymous seat creation is rejected without changing inventory