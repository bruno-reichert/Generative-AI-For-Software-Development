from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple in-memory inventory
inventory = {
    "101": {"title": "The Hobbit", "stock": 5, "price": 10.99},
    "102": {"title": "1984", "stock": 2, "price": 8.99}
}

@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    """Retrieves a book's details by ID. Safely handles missing IDs."""
    # Defensive Check: Verify the book exists before accessing it
    if id not in inventory:
        return jsonify({"error": "Book not found"}), 404
        
    return jsonify(inventory[id]), 200

@app.route('/purchase', methods=['POST'])
def purchase_book():
    """Purchases a book from the inventory with input and stock validation."""
    data = request.get_json() or {}
    book_id = data.get('id')
    quantity = data.get('quantity', 1)

    # 1. Validation: Verify the book exists
    if not book_id or book_id not in inventory:
        return jsonify({"error": "Book not found"}), 404

    # 2. Validation: Prevent negative or zero quantities
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    book = inventory[book_id]

    # 3. Validation: Verify we have enough stock
    if book['stock'] < quantity:
        return jsonify({"error": "Insufficient stock available"}), 400

    # Process secure stock deduction
    book['stock'] -= quantity
    total_cost = round(book['price'] * quantity, 2)

    return jsonify({
        "message": "Purchase successful", 
        "total_cost": total_cost, 
        "remaining_stock": book['stock']
    }), 200

@app.route('/add_stock', methods=['POST'])
def add_stock():
    """Adds stock to an existing book with input validation and JSON response."""
    data = request.get_json() or {}
    book_id = data.get('id')
    amount = data.get('amount')

    # 1. Validation: Verify the book exists
    if not book_id or book_id not in inventory:
        return jsonify({"error": "Book not found"}), 404

    # 2. Validation: Prevent adding negative or zero stock amount
    if not isinstance(amount, int) or amount <= 0:
        return jsonify({"error": "Amount must be a positive integer"}), 400

    inventory[book_id]['stock'] += amount
    
    # Consistency Fix: Return JSON instead of plain text on success
    return jsonify({
        "message": "Stock added successfully",
        "new_stock": inventory[book_id]['stock']
    }), 200

@app.route('/inventory', methods=['GET'])
def list_inventory():
    """Lists all books in the inventory."""
    return jsonify(inventory), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)