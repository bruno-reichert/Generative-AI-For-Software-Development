from sqlalchemy import create_engine, text

# 1. Initialize the engine
# 'echo=True' will print all raw SQL commands to the terminal (excellent for learning)
engine = create_engine('sqlite:///ecommerce.db', echo=True)

print("Attempting to connect to the database...")

# 2. Force a connection test using the 'with' statement for safe resource handling
try:
    with engine.connect() as connection:
        # text() is required in SQLAlchemy 2.0 to execute raw SQL strings safely
        query = text("SELECT 1")
        result = connection.execute(query).fetchone()
        
        # Verify we received our test value back (should print (1,))
        print("\n--- Connection Success! ---")
        print(f"Database returned: {result}")
        print("----------------------------\n")
        
except Exception as e:
    print("\n--- Connection Failed ---")
    print(f"Error details: {e}")
    print("-------------------------\n")