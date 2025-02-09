import pytest
from app import app

@pytest.fixture
def client():
    # Set up a test client for the Flask app
    with app.test_client() as client:
        yield client

def test_process_receipt_valid(client):
    """
    Test processing a valid receipt.
    Expected: A JSON response with a receipt ID.
    """
    payload = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "total": "35.35",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
            {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
            {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
            {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
            {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"}
        ]
    }
    response = client.post('/receipts/process', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "id" in data

def test_get_points_valid(client):
    """
    Test retrieving points for a valid receipt.
    Expected: The points calculated match the expected value.
    """
    payload = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "total": "35.35",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
            {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
            {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
            {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
            {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"}
        ]
    }
    # Process the receipt and retrieve the receipt ID
    post_response = client.post('/receipts/process', json=payload)
    post_data = post_response.get_json()
    receipt_id = post_data["id"]

    # Retrieve points using the receipt ID
    get_response = client.get(f'/receipts/{receipt_id}/points')
    get_data = get_response.get_json()
    assert get_response.status_code == 200
    # Expected points: 28 (based on the provided calculation rules)
    assert "points" in get_data
    assert get_data["points"] == 28

def test_process_receipt_missing_field(client):
    """
    Test processing a receipt with a missing required field.
    Expected: A 400 error with an error message containing 'Please verify input.'
    """
    # Omit the 'retailer' field
    payload = {
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "total": "35.35",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"}
        ]
    }
    response = client.post('/receipts/process', json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert "Please verify input." in data["error"]

def test_process_receipt_invalid_json(client):
    """
    Test processing a receipt with invalid JSON payload.
    Expected: A 400 error with an error message containing 'Please verify input.'
    """
    response = client.post('/receipts/process', data="Not a JSON", content_type='application/json')
    data = response.get_json()
    assert response.status_code == 400
    assert "Please verify input." in data["error"]

def test_get_points_not_found(client):
    """
    Test retrieving points for a non-existent receipt.
    Expected: A 404 error with an error message.
    """
    response = client.get('/receipts/non-existent-id/points')
    data = response.get_json()
    assert response.status_code == 404
    assert "No receipt found for that ID." in data["error"]

def test_second_sample_receipt(client):
    """
    Test the second sample receipt provided in the specification.
    Expected: The points calculated should be 109.
    """
    payload = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "total": "9.00",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"}
        ]
    }
    post_response = client.post('/receipts/process', json=payload)
    post_data = post_response.get_json()
    receipt_id = post_data["id"]

    get_response = client.get(f'/receipts/{receipt_id}/points')
    get_data = get_response.get_json()
    assert get_response.status_code == 200
    assert get_data["points"] == 109
