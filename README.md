# GelberQAChallenge

This project is a QA Automation challenge using Python and Behave to test a RESTful Booking API. The tests validate the API’s functionality, covering booking creation, updates, retrieval, and deletion.

## Project Overview

The project is structured using Behavior Driven Development (BDD) to ensure the quality of the Booking API. The tests cover range of scenarios, including:
- Verifying API availability
- Creating bookings with valid and invalid data
- Retrieving booking information
- Updating and partially updating bookings
- Deleting bookings and handling non-existing booking deletions

## Project Setup

### Prerequisites

- **Python 3.8+** installed
- **Behave** for Behavior-Driven Development (BDD)
- **Requests** library for API interactions

### Installation

1. **Clone the repository**:
   
   ```bash
   git clone <https://github.com/hasannsahin11/GelberQAChallenge.git>   
   cd GelberQAChallenge

2. **Set up a virtual environment**:

   python -m venv venv
   source venv/bin/activate       # On Windows use `venv\Scripts\activate`

3. **Install the required dependencies**:
   pip install -r requirements.txt


## Directory Structure

GelberQAChallenge/
│
├── features/
│   ├── booking.feature       # Contains all test scenarios
│   ├── environment.py        # Behave environment configuration
│   └── steps/
│       └── booking_steps.py  # Step definitions for the scenarios
│
└── README.md                 # Project documentation

## Running the Tests

1. **Activate the virtual environment**:
   source venv/bin/activate       # On Windows use `venv\Scripts\activate`

2. **Run Behave**:
  
    behave

    Alternatively, if you want to see the print statements directly in the console, use:

    behave --no-capture
