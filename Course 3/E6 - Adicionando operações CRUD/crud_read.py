from sqlalchemy import select
from sqlalchemy.orm import Session
from create_schema import engine, User, Product

print("\n--- Executing ADVANCED READ Queries ---")

with Session(engine) as session:
    # =====================================================================
    # Query 1: Direct Lookup by Primary Key (O(1) complexity)
    # =====================================================================
    user_id = 1
    # session.get() instantly pulls User ID 1
    user_by_id = session.get(User, user_id)
    
    print(f"[Query 1] Lookup by ID ({user_id}):")
    if user_by_id:
        print(f"  Found! Username: {user_by_id.username} | Email: {user_by_id.email}")
    else:
        print(f"  User with ID {user_id} not found.")

    # =====================================================================
    # Query 2: Filtering with .where() (SQL WHERE clause)
    # =====================================================================
    target_username = "alice_dev"
    # SELECT * FROM users WHERE username = 'alice_dev'
    query = select(User).where(User.username == target_username)
    
    # We use .scalar() instead of .scalars().all() because we only expect ONE unique result
    user_by_username = session.scalar(query)
    
    print(f"\n[Query 2] Filter by Username ('{target_username}'):")
    if user_by_username:
        print(f"  Found! Email: {user_by_username.email} | Created At: {user_by_username.created_at}")
    else:
        print(f"  No user found with username '{target_username}'")

print("\n--- READ Operations Complete! ---")