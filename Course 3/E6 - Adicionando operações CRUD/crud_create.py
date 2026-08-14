from decimal import Decimal
from sqlalchemy.orm import Session
# Import our database engine, Session manager, and table classes from yesterday
from create_schema import engine, User, Product

# =====================================================================
# 1. Reusable Creation Functions
# =====================================================================

def create_user(session: Session, username: str, email: str) -> User:
    """
    Creates a new user in the database.
    """
    new_user = User(username=username, email=email)
    session.add(new_user)
    # We commit the transaction to save the user permanently
    session.commit()
    # After committing, SQLAlchemy automatically updates our 'new_user' 
    # object with its newly generated database ID!
    return new_user


def create_product(session: Session, name: str, price: float, stock: int) -> Product:
    """
    Creates a new product in the database.
    """
    # Convert the price float to a Decimal for financial precision
    decimal_price = Decimal(str(price))
    new_product = Product(name=name, price=decimal_price, stock=stock)
    
    session.add(new_product)
    session.commit()
    return new_product


# =====================================================================
# 2. Executing the "Create" Operations
# =====================================================================
if __name__ == "__main__":
    print("\n--- Executing CREATE Operations ---")

    # Open a safe, transactional Session context
    with Session(engine) as session:
        # Create a new user
        print("Creating User 'alice_dev'...")
        alice = create_user(session, username="alice_dev", email="alice@example.com")
        print(f"Success! Created User ID: {alice.id}")

        # Create some products
        print("\nCreating Products...")
        laptop = create_product(session, name="Developer Laptop", price=1200.00, stock=5)
        coffee_maker = create_product(session, name="Drip Coffee Maker", price=79.99, stock=15)
        notebook = create_product(session, name="Paper Notebook", price=4.50, stock=50)

        print(f"Success! Created Product IDs:")
        print(f"  - {laptop.name} (ID: {laptop.id})")
        print(f"  - {coffee_maker.name} (ID: {coffee_maker.id})")
        print(f"  - {notebook.name} (ID: {notebook.id})")

    print("\n--- CREATE Operations Complete! ---")