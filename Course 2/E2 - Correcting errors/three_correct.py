import hashlib
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Simple in-memory user database
users_db = {}


# =====================================================================
# Pydantic Schemas (Input vs. Output Separation)
# =====================================================================

class UserCreate(BaseModel):
    """Schema for creating a user (accepts password)."""
    id: int
    username: str
    email: EmailStr  # EmailStr validates that the email format is correct
    password: str


class UserResponse(BaseModel):
    """Schema for returning user data (strips password completely)."""
    id: int
    username: str
    email: EmailStr


# =====================================================================
# Password Hashing Helper
# =====================================================================
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 with a static salt for local testing."""
    salt = "secure_salt_value"
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed


# =====================================================================
# Route Handlers
# =====================================================================

# 1. Configured status_code=201 for creation
# 2. Configured response_model=UserResponse so FastAPI strips out the password automatically
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Creates a new user, hashes their password, and returns public details."""
    if user.id in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User ID already exists"
        )

    # Convert the Pydantic model to a standard dictionary (using V2 model_dump)
    user_data = user.model_dump()
    
    # Hash the password before saving
    user_data["password"] = hash_password(user_data["password"])
    
    # Save to mock DB
    users_db[user.id] = user_data
    
    # Return the dictionary. FastAPI will automatically convert it 
    # to a UserResponse object, hiding the password!
    return user_data


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """Retrieves a user by ID. Returns 404 if missing."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return users_db[user_id]


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    """Updates an existing user's details. Returns 404 if missing."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    user_data = user.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    
    users_db[user_id] = user_data
    return user_data


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Deletes a user. Returns 404 if missing."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    del users_db[user_id]
    return {"message": "User deleted"}