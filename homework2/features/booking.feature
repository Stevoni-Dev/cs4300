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