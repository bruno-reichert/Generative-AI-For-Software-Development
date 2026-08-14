from sqlalchemy.orm import Session
# Import our models and engine
from create_schema import engine, Product

print("\n--- Executing DELETE Operation ---")

with Session(engine) as session:
    # 1. READ: Find the product we want to delete (ID 2 is the Coffee Maker)
    product_id = 2
    coffee_maker = session.get(Product, product_id)
    
    if coffee_maker:
        print(f"Found product: '{coffee_maker.name}' (ID: {coffee_maker.id})")
        
        # 2. DELETE: Mark the object for deletion in the session
        print(f"Deleting '{coffee_maker.name}' from the session...")
        session.delete(coffee_maker)
        
        # 3. COMMIT: Apply the deletion permanently in SQL
        print("Committing transaction...")
        session.commit()  # SQLAlchemy executes the SQL 'DELETE FROM' here!
        
        print("\nDelete Complete!")
    else:
        print(f"Product with ID {product_id} not found.")

# =====================================================================
# Verification: Try to read it back
# =====================================================================
print("\n--- Verification (Attempting to read deleted product) ---")
with Session(engine) as session:
    deleted_product = session.get(Product, product_id)
    
    # We expect 'deleted_product' to be None because it no longer exists
    if deleted_product is None:
        print(f"Success! Product with ID {product_id} is no longer in the database.")
    else:
        print(f"Warning: Product still exists: {deleted_product.name}")
print("-----------------------------------------------------------\n")