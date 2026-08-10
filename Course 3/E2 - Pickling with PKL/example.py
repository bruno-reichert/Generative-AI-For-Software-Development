import pickle

# A custom Python class to demonstrate that Pickle can serialize complex objects
class PlayerCharacter:
    def __init__(self, name, level, inventory):
        self.name = name
        self.level = level
        self.inventory = inventory

    def display_stats(self):
        print(f"Player: {self.name} | Level: {self.level} | Items: {self.inventory}")

# Create a live instance of our custom class
hero = PlayerCharacter("Aragorn", 10, ["Anduril", "Elven Cloak"])


# =====================================================================
# PART 1: Working with Files (dump and load)
# =====================================================================
# Note: Because Pickle converts objects to binary data, we MUST use 
# binary mode ('wb' for write-binary, 'rb' for read-binary).

# 1. pickle.dump(): Write the object directly to a file
with open("save_state.pkl", "wb") as file:
    pickle.dump(hero, file)
print("Successfully dumped 'hero' object to save_state.pkl")

# 2. pickle.load(): Read the object back from a file
with open("save_state.pkl", "rb") as file:
    loaded_hero = pickle.load(file)
print("Successfully loaded object from save_state.pkl")
# Verify it's a fully functional Python object by calling its method:
loaded_hero.display_stats()
print()


# =====================================================================
# PART 2: Working with In-Memory Bytes (dumps and loads)
# =====================================================================

# 3. pickle.dumps(): Convert the object to an in-memory byte stream
byte_stream = pickle.dumps(hero)
print("In-Memory Bytes representation:")
print(byte_stream)  # Prints raw, unreadable binary data (starting with b'\x80...')
print()

# 4. pickle.loads(): Convert a byte stream back into a live Python object
reconstructed_hero = pickle.loads(byte_stream)
print("Successfully reconstructed object from in-memory bytes:")
reconstructed_hero.display_stats()