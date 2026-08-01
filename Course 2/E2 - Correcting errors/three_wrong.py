from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Simple in-memory user database
users_db = {}

# Pydantic model for User data (used for both input and output)
class User(BaseModel):
    id: int
    username: str
    email: str
    password: str

@app.post("/users")
def create_user(user: User):
    """Creates a new user in the database."""
    # Process and save the user
    users_db[user.id] = user.dict()
    return users_db[user.id]

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Retrieves a user by their ID."""
    user = users_db.get(user_id)
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    """Updates an existing user's details."""
    users_db[user_id] = user.dict()
    return users_db[user_id]

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Deletes a user from the database."""
    if user_id in users_db:
        del users_db[user_id]
    return {"message": "User deleted"}