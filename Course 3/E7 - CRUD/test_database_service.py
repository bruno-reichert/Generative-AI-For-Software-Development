import unittest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import our schema base, tables, and all CRUD functions
from crud_superfile import (
    Base, User, Product, Order, OrderItem,
    create_user, create_product, create_order, add_item_to_order,
    get_user_by_id, get_user_by_username, get_product_by_id, get_product_by_id_cached,
    get_order_by_id, get_orders_by_user_id, get_user_order_manifest, get_most_ordered_product,
    update_product_stock_and_price, update_user_email, update_order_status, modify_order_item,
    delete_product, delete_user, delete_order, delete_order_item, _PRODUCT_CACHE
)

class TestDatabaseService(unittest.TestCase):

    def setUp(self):
        """
        Runs before EVERY single test.
        Creates a brand-new, in-memory SQLite database and seeds it with test data.
        """
        # Create in-memory engine
        self.test_engine = create_engine("sqlite://", echo=False)
        Base.metadata.create_all(self.test_engine)
        self.session = Session(self.test_engine)

        # Clear our caching dictionary before each test to ensure accurate cache testing
        _PRODUCT_CACHE.clear()

        # Seed initial test data
        self.alice = create_user(self.session, username="alice_dev", email="alice@example.com")
        self.bob = create_user(self.session, username="bob_bakes", email="bob@example.com")
        
        self.laptop = create_product(self.session, name="Developer Laptop", price=1200.00, stock=5)
        self.notebook = create_product(self.session, name="Paper Notebook", price=4.50, stock=50)

        # Alice places an order for 1 Laptop and 2 Notebooks
        self.order_alice = create_order(self.session, user_id=self.alice.id, status="pending")
        add_item_to_order(self.session, order_id=self.order_alice.id, product_id=self.laptop.id, quantity=1)
        add_item_to_order(self.session, order_id=self.order_alice.id, product_id=self.notebook.id, quantity=2)

    def tearDown(self):
        """Runs after EVERY single test. Closes the session and wipes the in-memory database."""
        self.session.close()
        Base.metadata.drop_all(self.test_engine)
        # Poland-Grade Polish: Explicitly dispose of the connection pool to silence ResourceWarnings
        self.test_engine.dispose()

    # =====================================================================
    # 1. READ & CACHING TESTS
    # =====================================================================

    def test_query_user_by_username(self):
        """Verify we can fetch a user by their unique username."""
        retrieved_user = get_user_by_username(self.session, "alice_dev")
        # Type Guard: Tells Pylance retrieved_user is definitely not None
        assert retrieved_user is not None
        self.assertEqual(retrieved_user.email, "alice@example.com")

    def test_product_query_cache_hit_and_miss(self):
        """Verify that the cache successfully saves database accesses."""
        product_first = get_product_by_id_cached(self.session, self.laptop.id)
        self.assertIn(self.laptop.id, _PRODUCT_CACHE)

        product_second = get_product_by_id_cached(self.session, self.laptop.id)
        self.assertEqual(product_first, product_second)

    def test_most_ordered_product_aggregation(self):
        """Verify the database correctly calculates the most-ordered product."""
        result = get_most_ordered_product(self.session)
        # Type Guard: Tell Pylance result is not None before unpacking
        assert result is not None
        name, total_qty = result
        self.assertEqual(name, "Paper Notebook")
        self.assertEqual(total_qty, 2)

    def test_user_order_manifest(self):
        """Verify the detailed order manifest prints correctly."""
        manifest = get_user_order_manifest(self.session, self.alice.id)
        self.assertEqual(len(manifest), 2)  # Laptop and Notebooks
        self.assertEqual(manifest[0]["product_name"], "Developer Laptop")
        self.assertEqual(manifest[1]["product_name"], "Paper Notebook")

    # =====================================================================
    # 2. UPDATE & BUSINESS LOGIC TESTS
    # =====================================================================

    def test_update_product_invalidates_cache(self):
        """Verify that updating a product successfully purges stale cache data."""
        get_product_by_id_cached(self.session, self.laptop.id)
        self.assertIn(self.laptop.id, _PRODUCT_CACHE)

        update_product_stock_and_price(self.session, self.laptop.id, new_stock=3, new_price=1100.00)
        self.assertNotIn(self.laptop.id, _PRODUCT_CACHE)

    def test_modify_order_item_orchestrator(self):
        """Verify our high-level Cart Manager handle additions, updates, and removals."""
        # Case A: Update quantity of notebooks in Alice's order from 2 to 5
        modify_order_item(self.session, self.order_alice.id, self.notebook.id, action="update", quantity=5)
        
        # Check order item quantity
        order = get_order_by_id(self.session, self.order_alice.id)
        # Type Guard: Tell Pylance order is not None
        assert order is not None
        self.assertEqual(order.items[1].quantity, 5)

        # Case B: Remove laptop from Alice's order
        modify_order_item(self.session, self.order_alice.id, self.laptop.id, action="remove")
        self.assertEqual(len(order.items), 1)  # Only notebooks should remain

        # Case C: Prevent adding 0 or negative quantities
        with self.assertRaises(ValueError):
            modify_order_item(self.session, self.order_alice.id, self.notebook.id, action="add", quantity=-10)

    # =====================================================================
    # 3. DELETE & CASCADE INTEGRITY TESTS
    # =====================================================================

    def test_delete_user_triggers_cascade_deletes(self):
        """Verify that deleting a User automatically deletes their orders (Cascade)."""
        alice_orders = get_orders_by_user_id(self.session, self.alice.id)
        self.assertEqual(len(alice_orders), 1)

        success = delete_user(self.session, self.alice.id)
        self.assertTrue(success)

        self.assertIsNone(get_user_by_id(self.session, self.alice.id))

        # CRUCIAL CASCADE CHECK: Alice's order must be automatically deleted from the database
        orders_query = self.session.get(Order, self.order_alice.id)
        self.assertIsNone(orders_query)


if __name__ == "__main__":
    unittest.main()