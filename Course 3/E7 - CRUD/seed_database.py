from sqlalchemy.orm import Session
# Import our unified engine, base metadata, and CRUD functions from the SUPERFILE
from crud_superfile import (
    Base, engine, 
    create_user, create_product, create_order, add_item_to_order
)

def seed_database():
    """
    Wipes the database and populates it with a complete, multi-table e-commerce dataset.
    """
    print("Wiping existing database to ensure a clean slate...")
    # Drop all existing tables (clears out old data)
    Base.metadata.drop_all(engine)
    # Recreate the tables cleanly with our newly defined indexes
    Base.metadata.create_all(engine)
    print("Database structure successfully re-initialized.")

    print("\nStarting database seeding process...")
    with Session(engine) as session:
        # =====================================================================
        # 1. Populate 'users' Table
        # =====================================================================
        print("Inserting Users...")
        alice = create_user(session, username="alice_dev", email="alice@example.com")
        bob = create_user(session, username="bob_bakes", email="bob@example.com")
        charlie = create_user(session, username="charlie_travels", email="charlie@example.com")

        # =====================================================================
        # 2. Populate 'products' Table
        # =====================================================================
        print("Inserting Products...")
        laptop = create_product(session, name="Developer Laptop", price=1200.00, stock=5)
        coffee_maker = create_product(session, name="Drip Coffee Maker", price=79.99, stock=15)
        notebook = create_product(session, name="Paper Notebook", price=4.50, stock=50)
        smartphone = create_product(session, name="NextGen Smartphone", price=699.99, stock=10)

        # =====================================================================
        # 3. Populate 'orders' & 'order_items' Tables (Relational Data)
        # =====================================================================
        print("Generating Orders and Order Items...")
        
        # Order 1: Alice buys 1 Laptop and 2 Notebooks
        order_alice = create_order(session, user_id=alice.id, status="completed")
        add_item_to_order(session, order_id=order_alice.id, product_id=laptop.id, quantity=1)
        add_item_to_order(session, order_id=order_alice.id, product_id=notebook.id, quantity=2)

        # Order 2: Bob buys 1 Coffee Maker
        order_bob = create_order(session, user_id=bob.id, status="shipped")
        add_item_to_order(session, order_id=order_bob.id, product_id=coffee_maker.id, quantity=1)

        # Order 3: Charlie buys 1 Smartphone and 1 Notebook
        order_charlie = create_order(session, user_id=charlie.id, status="pending")
        add_item_to_order(session, order_id=order_charlie.id, product_id=smartphone.id, quantity=1)
        add_item_to_order(session, order_id=order_charlie.id, product_id=notebook.id, quantity=1)

        print("\nDatabase seeding completed successfully!")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"\n[Seeding Error] Process aborted: {e}")