from sqlalchemy import select
from sqlalchemy.orm import Session
# Import our models, engine, and our new helper
from crud_superfile import engine, OrderItem, explain_query

with Session(engine) as session:
    print("==================================================")
    print("        DEBUGGING WITH EXPLAIN QUERY PLAN         ")
    print("==================================================")

    # --- Query A: Searching by index columns ---
    print("\n[Query A] Searching order_items by order_id & product_id:")
    stmt_a = select(OrderItem).where(
        OrderItem.order_id == 1, 
        OrderItem.product_id == 1
    )
    
    plan_a = explain_query(session, stmt_a)
    print(plan_a)
    # Expected output: Should mention using the index 'ix_order_items_order_product'

    # --- Query B: Searching by un-indexed column ---
    print("\n[Query B] Searching order_items by quantity (un-indexed):")
    stmt_b = select(OrderItem).where(
        OrderItem.quantity == 2
    )
    
    plan_b = explain_query(session, stmt_b)
    print(plan_b)
    # Expected output: Should mention a "SCAN table" (Table Scan) because there is no index!
    
    print("==================================================")