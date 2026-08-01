import unittest
# Import FastAPI's built-in TestClient
from fastapi.testclient import TestClient
# Import the app and database from our module
from three_correct import app, users_db

class TestFastAPIUserAPI(unittest.TestCase):

    def setUp(self):
        """Runs before every test. Sets up the TestClient and resets the DB."""
        self.client = TestClient(app)
        users_db.clear()

    # -----------------------------------------------------------------
    # FAIL CASE 1: POST /users should return 201 Created (Currently returns 200)
    # -----------------------------------------------------------------
    def test_create_user_status_code(self):
        print("\n[Running Test] Checking user creation HTTP status code...")
        payload = {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "password": "supersecurepassword123"
        }
        response = self.client.post("/users", json=payload)
        # We expect a 201 Created status code for successful creation
        self.assertEqual(response.status_code, 201)

    # -----------------------------------------------------------------
    # FAIL CASE 2: API should NOT leak passwords in response schemas
    # -----------------------------------------------------------------
    def test_create_user_does_not_leak_password(self):
        print("\n[Running Test] Checking for password leakage in response...")
        payload = {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "password": "supersecurepassword123"
        }
        response = self.client.post("/users", json=payload)
        data = response.json()
        
        # The password field should be completely absent from the response
        self.assertNotIn("password", data)

    # -----------------------------------------------------------------
    # FAIL CASE 3: Database should NOT store passwords in plaintext
    # -----------------------------------------------------------------
    def test_password_is_hashed_in_db(self):
        print("\n[Running Test] Checking for plaintext password storage...")
        payload = {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "password": "supersecurepassword123"
        }
        self.client.post("/users", json=payload)
        
        # Check the database directly to verify the password was hashed
        stored_user = users_db[1]
        self.assertNotEqual(stored_user["password"], "supersecurepassword123")

    # -----------------------------------------------------------------
    # FAIL CASE 4: GET /users/{user_id} should return 404 on missing ID (Currently 200 null)
    # -----------------------------------------------------------------
    def test_get_user_not_found(self):
        print("\n[Running Test] Checking missing user GET requests...")
        response = self.client.get("/users/999")
        # We expect a 404 Not Found error, but the current code will return 200 OK with null
        self.assertEqual(response.status_code, 404)

    # -----------------------------------------------------------------
    # FAIL CASE 5: PUT /users/{user_id} should return 404 on missing ID
    # -----------------------------------------------------------------
    def test_update_user_not_found(self):
        print("\n[Running Test] Checking missing user PUT requests...")
        payload = {
            "id": 999,
            "username": "ghost",
            "email": "ghost@example.com",
            "password": "somepassword"
        }
        response = self.client.put("/users/999", json=payload)
        # We expect a 404 Not Found error, but the current code allows updating non-existent IDs
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()