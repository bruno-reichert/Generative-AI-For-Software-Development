from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple in-memory inventory
inventory = {
    "101": {"title": "The Hobbit", "stock": 5, "price": 10.99},
    "102": {"title": "1984", "stock": 2, "price": 8.99}
}

@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    """Retrieves a book's details by ID."""
    book = inventory[id]
    return jsonify(book)

@app.route('/purchase', methods=['POST'])
def purchase_book():
    """Purchases a book from the inventory."""
    data = request.get_json()
    book_id = data.get('id')
    quantity = data.get('quantity', 1)  # Default quantity is 1

    # Fetch the book details
    book = inventory[book_id]

    # Process stock deduction
    book['stock'] -= quantity
    total_cost = book['price'] * quantity

    return jsonify({
        "message": "Purchase successful", 
        "total_cost": total_cost, 
        "remaining_stock": book['stock']
    })

@app.route('/add_stock', methods=['POST'])
def add_stock():
    """Adds stock to an existing book."""
    data = request.get_json()
    book_id = data.get('id')
    amount = data.get('amount')

    if book_id in inventory:
        inventory[book_id]['stock'] += amount
        return "Stock added successfully"
    else:
        return jsonify({"error": "Book not found"}), 404

@app.route('/inventory', methods=['GET'])
def list_inventory():
    """Lists all books in the inventory."""
    return jsonify(inventory)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)