Feature: Booking API Validation

  Scenario: Verify that the booking API is available
    Given the booking API is available
    Then I should receive a successful health check response

  Scenario: Create a booking with valid data
    Given the booking API is available
    When I create a booking with the following details:
      | firstname | lastname | totalprice | depositpaid | checkin    | checkout   | additionalneeds |
      | John      | Doe      | 150        | true        | 2024-11-01 | 2024-11-10 | Breakfast       |
    Then the booking should be created successfully

  Scenario: Create a booking with invalid data
    Given the booking API is available
    When I create a booking with the following invalid details:
      | firstname | lastname | totalprice | depositpaid | checkin    | checkout   | additionalneeds |
      |           |          | 150        | true        | 2024-11-01 | 2024-11-10 | Breakfast       |
    Then I should receive a client error response

  Scenario: Retrieve all booking IDs
    Given the booking API is available
    When I request all booking IDs
    Then I should receive a list of booking IDs

  Scenario: Retrieve booking IDs by query with names
    Given the booking API is available
    When I request booking IDs filtered by:
      | firstname | lastname |
      | John      | Doe      |
    Then I should receive a filtered list of booking IDs

  Scenario: Retrieve a single booking by ID
    Given the booking API is available
    When I retrieve the booking details with a previously created booking ID
    Then I should see the correct booking details

  Scenario: Update an expired booking
    Given an expired booking is available
    When I try to update the expired booking with the following details:
      | firstname | lastname | totalprice | depositpaid | checkin    | checkout   | additionalneeds |
      | Alice     | Johnson  | 200        | false       | 2024-11-01 | 2024-11-02 | Late Checkout   |
    Then the update should be rejected

Scenario: Partially update a booking
    Given a valid booking is available
    When I partially update the created booking with the following details:
      | firstname | lastname |
      | Michael   | Smith    |
    Then the booking should be partially updated successfully

Scenario: Delete a booking
    Given a valid booking is available
    When I delete the created booking
    Then the booking should be deleted successfully

 Scenario: Delete a non-existing booking
    Given a previously deleted booking ID is available
    When I try to delete the non-existing booking
    Then the deletion attempt should fail with a not found error