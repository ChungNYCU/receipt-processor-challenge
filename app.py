from flask import Flask, request, jsonify
from uuid import uuid4
from decimal import Decimal, ROUND_UP
from datetime import datetime, time

app = Flask(__name__)

# In-memory storage for receipts
receipts = {}

def calculate_points(receipt):
    """
    Calculates the points awarded for a given receipt based on the following rules:
    
    1. One point for every alphanumeric character in the retailer name.
    2. 50 points if the total is a round dollar amount with no cents.
    3. 25 points if the total is a multiple of 0.25.
    4. 5 points for every two items on the receipt.
    5. For each item, if the trimmed item description length is a multiple of 3,
       multiply the item price by 0.2 and round up to the nearest integer; add that value.
    6. 6 points if the day in the purchase date is odd.
    7. 10 points if the time of purchase is between 14:00 (inclusive) and 16:00 (exclusive).
    """
    points = 0

    # Rule 1: Add one point for every alphanumeric character in the retailer name.
    retailer = receipt.get("retailer", "")
    points += sum(1 for c in retailer if c.isalnum())

    # Rule 2: Add 50 points if the total is a round dollar amount (no cents).
    try:
        total = Decimal(receipt.get("total", "0.00"))
    except Exception:
        total = Decimal("0.00")
    if total == total.to_integral_value():
        points += 50

    # Rule 3: Add 25 points if the total is a multiple of 0.25.
    if total % Decimal("0.25") == 0:
        points += 25

    # Rule 4: Add 5 points for every two items on the receipt.
    items = receipt.get("items", [])
    points += (len(items) // 2) * 5

    # Rule 5: For each item, if the trimmed description length is a multiple of 3,
    #         multiply the price by 0.2 and round up to get the points for that item.
    for item in items:
        description = item.get("shortDescription", "").strip()
        if len(description) % 3 == 0:
            try:
                price = Decimal(item.get("price", "0.00"))
            except Exception:
                price = Decimal("0.00")
            item_points = (price * Decimal("0.2")).to_integral_value(rounding=ROUND_UP)
            points += int(item_points)

    # Rule 6: Add 6 points if the purchase day is odd.
    purchase_date = receipt.get("purchaseDate", "")
    try:
        dt = datetime.strptime(purchase_date, "%Y-%m-%d")
        if dt.day % 2 == 1:
            points += 6
    except Exception:
        pass

    # Rule 7: Add 10 points if the purchase time is between 14:00 (inclusive) and 16:00 (exclusive).
    purchase_time = receipt.get("purchaseTime", "")
    try:
        t = datetime.strptime(purchase_time, "%H:%M").time()
        if time(14, 0) <= t < time(16, 0):
            points += 10
    except Exception:
        pass

    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    # Ensure the request is JSON
    if not request.is_json:
        return jsonify({"error": "Please verify input. JSON required."}), 400
    try:
        receipt = request.get_json()
    except Exception:
        return jsonify({"error": "Please verify input. Invalid JSON."}), 400

    # Basic field validation
    required_fields = ["retailer", "purchaseDate", "purchaseTime", "items", "total"]
    for field in required_fields:
        if field not in receipt:
            return jsonify({"error": f"Please verify input. Missing field: {field}"}), 400

    # Generate a unique receipt ID
    receipt_id = str(uuid4())

    # Calculate the points for the receipt
    points = calculate_points(receipt)

    # Store the receipt and its calculated points in memory
    receipts[receipt_id] = {
        "receipt": receipt,
        "points": points
    }

    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    if receipt_id not in receipts:
        return jsonify({"error": "No receipt found for that ID."}), 404
    points = receipts[receipt_id]["points"]
    return jsonify({"points": points}), 200

if __name__ == '__main__':
    # Run the Flask app on port 5000 and listen on all interfaces
    app.run(host='0.0.0.0', port=5000)
