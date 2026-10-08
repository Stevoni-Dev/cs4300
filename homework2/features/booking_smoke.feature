@integration
Feature: Behave smoke test
  Scenario: The Django app is configured for behave tests
    Given the Django app is ready
    Then the settings module is configured
