# receipt-processor-challenge

This is a Receipt Processor web service built with Python 3, Flask, and Docker.

## API Endpoints
### POST /receipts/process
Submits a receipt for processing and returns a unique receipt ID.
Request Example: 
```
{
    "retailer": "Target", 
    "purchaseDate": "2022-01-01", 
    "purchaseTime": "13:01", 
    "total": "35.35", 
    "items":[ 
                { "shortDescription": "Mountain Dew 12PK", "price": "6.49" },
                { "shortDescription": "Emils Cheese Pizza", "price": "12.25" }
            ]
}
```

Response Example: 
```
{ "id": "7fb1377b-b223-49d9-a31a-5a02701dd310" }
```

### GET /receipts/{id}/points
Retrieves the number of points awarded for the receipt with the given ID.

Response Example: 
```
{ "points": 20 }
```

## Point Calculation Rules
Points are calculated using the following rules:

**Rule 1**: One point for every alphanumeric character in the retailer name.
**Rule 2**: Add 50 points if the total is a round dollar amount (no cents).
**Rule 3**: Add 25 points if the total is a multiple of 0.25.
**Rule 4**: Add 5 points for every two items on the receipt.
**Rule 5**: For each item, if the trimmed description length is a multiple of 3, multiply the price by 0.2, round up to the nearest integer, and add that value.
**Rule 6**: Add 6 points if the purchase day is odd.
**Rule 7**: Add 10 points if the purchase time is between 14:00 (inclusive) and 16:00 (exclusive).

## Running the Application with Docker
### Build the Docker Image
In the project directory, run: 
`docker build -t receipt-processor`.

### Run the Docker Container
Start the container by running: 
`docker run -p 5000:5000 receipt-processor`

The service will be available at `http://localhost:5000`.

## Running the Application Locally
### Setup venv and Install Dependencies
In the project directory, run: `setup.bat`

### Start the Flask Application
Run: `python app.py`
The service will be available at `http://localhost:5000`.

Error Handling
If the input is invalid (e.g., missing required fields or invalid JSON), the API will return a 400 error.
The error message will include the phrase "Please verify input." as required.
This repository provides a complete solution for the receipt processor coding challenge from `Fetch Rewards`. 