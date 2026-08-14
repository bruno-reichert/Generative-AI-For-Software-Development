from decimal import Decimal
from sqlalchemy.orm import Session
# Import our models and engine
from create_schema import engine, Product

print("\n--- Executing UPDATE Operation ---")

with Session(engine) as session:
    # 1. READ: First, find the product we want to update (ID 1 is the Laptop)
    laptop_id = 1
    laptop = session.get(Product, laptop_id)
    
    if laptop:
        print(f"Current State: {laptop.name} | Stock: {laptop.stock} | Price: ${laptop.price}")
        
        # 2. MODIFY: Update the stock and price directly as Python properties
        print("\nModifying product properties in Python...")
        laptop.stock = 4                      # Decrease stock by 1
        laptop.price = Decimal("1150.00")      # Put it on sale!
        
        # 3. COMMIT: Save the changes
        print("Committing transaction...")
        session.commit()  # SQLAlchemy detects the changes and runs the UPDATE SQL here!
        
        print("\nUpdate Complete!")
    else:
        print(f"Product with ID {laptop_id} not found.")

# =====================================================================
# Verification: Read it back to prove it saved
# =====================================================================
print("\n--- Verification (Reading back updated product) ---")
with Session(engine) as session:
    updated_laptop = session.get(Product, 1)
    if updated_laptop:
        print(f"Saved State: {updated_laptop.name} | Stock: {updated_laptop.stock} | Price: ${updated_laptop.price}")
print("---------------------------------------------------\n")