import unittest
import json
# Import the Flask application and the mock inventory
from two_correct import app, inventory

class TestBookAPI(unittest.TestCase):

    def setUp(self):
        """Runs before every test. Sets up the Flask test client."""
        self.client = app.test_client()
        
        # Reset the mock inventory to a clean state before each test
        inventory.clear()
        inventory.update({
            "101": {"title": "The Hobbit", "stock": 5, "price": 10.99},
            "102": {"title": "1984", "stock": 2, "price": 8.99}
        })

    # -----------------------------------------------------------------
    # FAIL CASE 1: KeyError on missing ID (Should return 404, not crash 500)
    # -----------------------------------------------------------------
    def test_get_book_not_found(self):
        """Test retrieving a book that does not exist."""
        print("\n[Running Test] Checking missing book error handling...")
        response = self.client.get('/book/999')
        # We expect a clean 404 Not Found error, but the current code will crash (500)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    # -----------------------------------------------------------------
    # FAIL CASE 2: Over-purchasing stock (Should block with 400, not go negative)
    # -----------------------------------------------------------------
    def test_purchase_exceeds_stock(self):
        """Test purchasing more copies than are in stock."""
        print("\n[Running Test] Checking over-purchasing validation...")
        payload = {"id": "101", "quantity": 10}  # Stock is only 5
        response = self.client.post('/purchase', json=payload)
        
        # We expect this to fail with a 400 Bad Request, but the current code allows it
        self.assertEqual(response.status_code, 400)

    # -----------------------------------------------------------------
    # FAIL CASE 3: The Negative Quantity exploit (Should block with 400)
    # -----------------------------------------------------------------
    def test_purchase_negative_quantity(self):
        """Test purchasing a negative quantity of books."""
        print("\n[Running Test] Checking negative quantity exploit...")
        payload = {"id": "101", "quantity": -5}
        response = self.client.post('/purchase', json=payload)
        
        # This should be blocked with a 400 Bad Request, but the current code allows it
        self.assertEqual(response.status_code, 400)

    # -----------------------------------------------------------------
    # FAIL CASE 4: The Negative Stock addition exploit (Should block with 400)
    # -----------------------------------------------------------------
    def test_add_negative_stock(self):
        """Test adding a negative amount of stock."""
        print("\n[Running Test] Checking negative stock addition...")
        payload = {"id": "101", "amount": -2}
        response = self.client.post('/add_stock', json=payload)
        
        # This should be blocked with a 400 Bad Request, but the current code allows it
        self.assertEqual(response.status_code, 400)

    # -----------------------------------------------------------------
    # FAIL CASE 5: Inconsistent API return format (Should return JSON)
    # -----------------------------------------------------------------
    def test_add_stock_success_format(self):
        """Test that the successful add_stock response is JSON, not plain text."""
        print("\n[Running Test] Checking API response format consistency...")
        payload = {"id": "101", "amount": 5}
        response = self.client.post('/add_stock', json=payload)
        
        # The API should return application/json
        self.assertEqual(response.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()