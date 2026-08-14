from sqlalchemy import select
from sqlalchemy.orm import Session
# Import our models and engine
from create_schema import engine, User, Product

print("\n--- Verifying Database Records (READ) ---")

# Open a read-only session
with Session(engine) as session:
    # 1. Query all users from the 'users' table
    # select(User) is the SQLAlchemy 2.0 standard way of writing "SELECT * FROM users"
    user_query = select(User)
    # session.scalars().all() executes the query and returns them as a Python list of User objects
    all_users = session.scalars(user_query).all()

    print(f"Total Users in Database: {len(all_users)}")
    for user in all_users:
        print(f"  - ID: {user.id} | Username: {user.username} | Email: {user.email}")

    # 2. Query all products from the 'products' table
    product_query = select(Product)
    all_products = session.scalars(product_query).all()

    print(f"\nTotal Products in Database: {len(all_products)}")
    for product in all_products:
        print(f"  - ID: {product.id} | Name: {product.name} | Price: ${product.price:.2f} | Stock: {product.stock}")

print("\n-----------------------------------------\n")