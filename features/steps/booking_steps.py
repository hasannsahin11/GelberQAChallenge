import json
from datetime import datetime

import requests
from behave import *

BASE_URL = "https://restful-booker.herokuapp.com"
TOKEN = None


@given("the booking API is available")
def step_impl(context):
    print("Checking if the API is available...")
    response = requests.get(f"{BASE_URL}/ping")
    context.response = response
    print(f"Response Status Code: {response.status_code}")


@then("I should receive a successful health check response")
def step_impl(context):
    print("Verifying the health check response...")
    assert context.response.status_code == 201, "API is not available"
    print(f"Response status code: {context.response.status_code}, API is available.")


# Function for booking creation
def create_booking(data):
    response = requests.post(f"{BASE_URL}/booking", json=data)
    return response


@when("I create a booking with the following details")
def step_impl(context):
    booking_data = {
        "firstname": context.table[0]['firstname'],
        "lastname": context.table[0]['lastname'],
        "totalprice": int(context.table[0]['totalprice']),
        "depositpaid": context.table[0]['depositpaid'].lower() == 'true',
        "bookingdates": {
            "checkin": context.table[0]['checkin'],
            "checkout": context.table[0]['checkout']
        },
        "additionalneeds": context.table[0]['additionalneeds']
    }

    context.response = create_booking(booking_data)
    context.booking_id = context.response.json().get('bookingid')

    # Storing the booking ID in shared data to use in the future
    context.shared_data['booking_id'] = context.booking_id


@then("the booking should be created successfully")
def step_impl(context):
    assert context.response.status_code == 200, "Booking creation failed"
    assert "bookingid" in context.response.json(), "Booking ID not returned"
    print(f"The booking has been created. Here is the booking ID: {context.booking_id}")
    print(f"Confirmed booking details: {context.response.json()}")


@when("I create a booking with the following invalid details")
def step_impl(context):
    booking_data = {
        "firstname": context.table[0]['firstname'],
        "lastname": context.table[0]['lastname'],
        "totalprice": int(context.table[0]['totalprice']),
        "depositpaid": context.table[0]['depositpaid'].lower() == 'true',
        "bookingdates": {
            "checkin": context.table[0]['checkin'],
            "checkout": context.table[0]['checkout']
        },
        "additionalneeds": context.table[0]['additionalneeds']
    }
    context.response = create_booking(booking_data)


@then("I should receive a client error response")
def step_impl(context):
    # Expecting a client error, typically status code 400
    assert context.response.status_code == 400, (f"Expected 400 but got {context.response.status_code}. It"
                                                 f"'s a BUG! Booking shouldn't be created without a name.")


@when("I request all booking IDs")
def step_impl(context):
    response = requests.get(f"{BASE_URL}/booking")
    context.response = response


@then("I should receive a list of booking IDs")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200 but got {context.response.status_code}"
    booking_ids = context.response.json()
    assert isinstance(booking_ids, list), "Booking IDs not returned as a list"
    assert len(booking_ids) > 0, "No booking IDs found"
    # If you would like to see the list of IDs please uncomment the code below
    # print(f"List of booking IDs: {booking_ids}")


@when("I request booking IDs filtered by")
def step_impl(context):
    firstname = context.table[0]['firstname']
    lastname = context.table[0]['lastname']

    response = requests.get(f"{BASE_URL}/booking", params={
        "firstname": firstname,
        "lastname": lastname
    })
    context.response = response


@then("I should receive a filtered list of booking IDs")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200 but got {context.response.status_code}"
    filtered_booking_ids = context.response.json()
    assert isinstance(filtered_booking_ids, list), "Filtered booking IDs not returned as a list"
    # If you would like to see the list of filtered IDs please uncomment the code below
    # print(f"Filtered Booking IDs: {filtered_booking_ids}")


@when("I retrieve the booking details with a previously created booking ID")
def step_impl(context):
    # Retrieving the booking details using the stored booking ID
    booking_id = context.shared_data.get('booking_id')
    assert booking_id is not None, "No booking ID available from previous scenario"

    response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    context.response = response


@then("I should see the correct booking details")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200 but got {context.response.status_code}"
    booking_data = context.response.json()

    expected_data = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 150,
        "depositpaid": True,
        "additionalneeds": "Breakfast"
    }

    # Validating the core booking data
    for key, expected_value in expected_data.items():
        assert booking_data[key] == expected_value, f"Expected {key} to be {expected_value} but got {booking_data[key]}"

    # Validating booking dates
    assert booking_data['bookingdates']['checkin'] == "2024-11-01", "Check-in date mismatch"
    assert booking_data['bookingdates']['checkout'] == "2024-11-10", "Check-out date mismatch"
    booking_id = context.shared_data.get('booking_id')
    print(f"Retrieved BookingID: {booking_id} and it"
          f"s details: {booking_data}")


@given("an expired booking is available")
def step_impl(context):
    # Retrieving all booking IDs
    response = requests.get(f"{BASE_URL}/booking")
    assert response.status_code == 200, "Failed to retrieve booking IDs"

    booking_ids = response.json()

    # Looking for an expired booking by checking the 'checkout' date
    expired_booking_id = None
    for booking in booking_ids:
        booking_id = booking['bookingid']
        booking_details_response = requests.get(f"{BASE_URL}/booking/{booking_id}")
        if booking_details_response.status_code == 200:
            booking_details = booking_details_response.json()
            checkout_date = booking_details['bookingdates']['checkout']
            # Checking if the checkout date is in the past
            if datetime.strptime(checkout_date, "%Y-%m-%d") < datetime.now():
                expired_booking_id = booking_id
                # Printing the booking details to see which booking we're trying to update
                print(f"The expired booking ID {expired_booking_id}:")
                print(json.dumps(booking_details, indent=4))
                break

    assert expired_booking_id is not None, "No expired booking found"
    context.booking_id = expired_booking_id


# Helper function to get an authentication token
def get_token():
    global TOKEN
    if TOKEN is None:
        response = requests.post(f"{BASE_URL}/auth", json={
            "username": "admin",
            "password": "password123"
        })
        TOKEN = response.json().get("token")
    return TOKEN


@when("I try to update the expired booking with the following details")
def step_impl(context):
    booking_data = {
        "firstname": context.table[0]['firstname'],
        "lastname": context.table[0]['lastname'],
        "totalprice": int(context.table[0]['totalprice']),
        "depositpaid": context.table[0]['depositpaid'].lower() == 'true',
        "bookingdates": {
            "checkin": context.table[0]['checkin'],
            "checkout": context.table[0]['checkout']
        },
        "additionalneeds": context.table[0]['additionalneeds']
    }

    # Using the stored expired booking ID to perform the update
    booking_id = context.booking_id
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={get_token()}"
    }
    response = requests.put(f"{BASE_URL}/booking/{booking_id}", json=booking_data, headers=headers)
    context.response = response


@then("the update should be rejected")
def step_impl(context):
    # Checking if the update was rejected, expecting a client or forbidden error
    assert context.response.status_code in [400,
                                            403], (f"Expected a rejection but got status code {context.response.status_code}, It"
                                                   f"'s a BUG!")

@given("a valid booking is available")
def step_impl(context):
        # Ensuring that we are using the booking from the "Create a booking with valid data" scenario
        booking_id = context.shared_data.get('booking_id')
        assert booking_id is not None, "No booking ID available from previous scenario"
        print(f"Using the existing valid booking with ID:  {booking_id}")


@when("I partially update the created booking with the following details")
def step_impl(context):
        partial_update_data = {
            "firstname": context.table[0]['firstname'],
            "lastname": context.table[0]['lastname']
        }

        # Storing the expected update data for verification later
        context.expected_partial_data = partial_update_data

        # Using the stored booking ID from the "Create a booking with valid data" scenario
        booking_id = context.shared_data.get('booking_id')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f"token={get_token()}"
        }
        # Sending a PATCH request to partially update the booking
        response = requests.patch(f"{BASE_URL}/booking/{booking_id}", json=partial_update_data, headers=headers)
        context.response = response

@then("the booking should be partially updated successfully")
def step_impl(context):
    # Checking if the patch request was successful
    assert context.response.status_code == 200, f"Partial booking update failed. Status code: {context.response.status_code}"

    # Validating that the updated fields match the expected values
    updated_booking = context.response.json()
    expected_data = context.expected_partial_data
    assert updated_booking['firstname'] == expected_data['firstname'], "First name did not update correctly"
    assert updated_booking['lastname'] == expected_data['lastname'], "Last name did not update correctly"

    # Displaying booking details after the partial update
    print("Updated booking details:")
    print(json.dumps(updated_booking, indent=4))


@when("I delete the created booking")
def step_impl(context):
    # Using the stored booking ID from the "Create a booking with valid data" scenario
    booking_id = context.shared_data.get('booking_id')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={get_token()}"
    }
    # Sending a DELETE request to delete the booking
    response = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    context.response = response


@then("the booking should be deleted successfully")
def step_impl(context):
    # Checking if the delete request was successful
    assert context.response.status_code == 201, f"Booking deletion failed. Status code: {context.response.status_code}"

    # Verifying that the booking no longer exists
    booking_id = context.shared_data.get('booking_id')
    response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert response.status_code == 404, "Booking still exists after deletion"

    # Print confirmation
    print(f"Booking with ID {booking_id} has been successfully deleted.")

@given("a previously deleted booking ID is available")
def step_impl(context):
    # Ensuring that we are using the booking created in the "Create a booking with valid data" scenario
    booking_id = context.shared_data.get('booking_id')
    assert booking_id is not None, "No booking ID found from the deleted booking scenario"
    print(f"Attempting to use previously deleted booking ID: {booking_id}")

@when("I try to delete the non-existing booking")
def step_impl(context):
    # Attempting to delete the already deleted booking using its booking ID
    booking_id = context.shared_data.get('booking_id')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={get_token()}"
    }
    # Sending a DELETE request for the non-existing booking
    response = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    context.response = response

@then("the deletion attempt should fail with a not found error")
def step_impl(context):
    booking_id = context.shared_data.get('booking_id')
    # Expecting a 404 Not Found or 405 Method Not Allowed response
    assert context.response.status_code in [404, 405], f"Expected 404 or 405 but got {context.response.status_code}"
    print(f"Deletion attempt failed as expected for non-existing booking ID {booking_id} with status code {context.response.status_code}.")