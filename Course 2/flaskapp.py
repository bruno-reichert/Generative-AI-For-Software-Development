"""
Secure User Management API
===========================
This is a secure implementation of a Flask user management application. 
It features schema-enforced validation, secure password hashing, protection 
against IDOR, database rollback on integrity failures, and safe network binding.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

# 1. Load configuration safely from .env environment file
load_dotenv()

app = Flask(__name__)

# Retrieve database URL dynamically from the system environment
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# =====================================================================
# Database Models & Schemas
# =====================================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Security Fix: Increased length to 255 to safely prevent truncation of modern hashes
    password = db.Column(db.String(255), nullable=False)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    # Security Fix: 
    # - Added load_only=True to prevent password hashes from leaking in GET requests
    # - Added max=128 to prevent long-input CPU-exhaustion DoS attacks on password hashing
    password = fields.Str(
        required=True, 
        load_only=True, 
        validate=validate.Length(min=6, max=128)
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Initialize database schemas
with app.app_context():
    db.create_all()


# =====================================================================
# Route Handlers
# =====================================================================

@app.route('/')
def home():
    return "Welcome to the Security Testing Demo!"


@app.route('/users', methods=['GET'])
def get_users():
    """
    Retrieves all users. Restricted to administrators to prevent user enumeration.
    """
    # Role-Based Access Control: Check if caller has administrator privileges
    user_role = request.headers.get('X-User-Role')
    if user_role != 'admin':
        return jsonify({"message": "Access denied. Administrator privileges required."}), 403

    try:
        users = User.query.all()
        result = users_schema.dump(users)
        return jsonify(result)
    except Exception:
        # Security Fix: Generic error message to prevent Information Disclosure
        return jsonify({"message": "An internal database error occurred while fetching users"}), 500


@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    """
    Retrieves a single user's public info (password is stripped by the schema).
    """
    user = User.query.get(id)
    if user:
        result = user_schema.dump(user)
        return jsonify(result)
    return jsonify({"message": "User not found"}), 404


@app.route('/user', methods=['POST'])
def add_user():
    """
    Registers a new user securely.
    """
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    
    # Transaction Protection Block
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        # Security Fix: If the username already exists, rollback to keep the session clean
        db.session.rollback()
        return jsonify({"message": "Username already exists. Please choose another."}), 400

    return jsonify({"message": "User added successfully"}), 201


@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    """
    Updates a user's details. Protected against IDOR.
    """
    # 1. Authentication Check: Verify who is calling
    auth_user_id_str = request.headers.get('X-Authenticated-User-ID')
    if not auth_user_id_str:
        return jsonify({"message": "Authentication is required to perform this action."}), 401

    try:
        auth_user_id = int(auth_user_id_str)
    except ValueError:
        return jsonify({"message": "Invalid authentication token format."}), 400

    # 2. Authorization Check: A user may ONLY update their own profile (IDOR Defense)
    if auth_user_id != id:
        return jsonify({"message": "You do not have permission to modify this user's profile."}), 403

    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    user = User.query.get(id)
    if user:
        user.username = data['username']
        user.password = generate_password_hash(data['password'])
        
        # Transaction Protection Block
        try:
            db.session.commit()
        except IntegrityError:
            # Prevent conflict if updating to an already existing username
            db.session.rollback()
            return jsonify({"message": "Username already exists. Please choose another."}), 400
            
        return jsonify({"message": "User updated successfully"})
        
    return jsonify({"message": "User not found"}), 404


@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Deletes a user account. Protected against IDOR.
    """
    # 1. Authentication Check
    auth_user_id_str = request.headers.get('X-Authenticated-User-ID')
    if not auth_user_id_str:
        return jsonify({"message": "Authentication is required to perform this action."}), 401

    try:
        auth_user_id = int(auth_user_id_str)
    except ValueError:
        return jsonify({"message": "Invalid authentication token format."}), 400

    # 2. Authorization Check (IDOR Defense)
    if auth_user_id != id:
        return jsonify({"message": "You do not have permission to delete this user."}), 403

    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"})
        
    return jsonify({"message": "User not found"}), 404


# =====================================================================
# Safe Application Runner
# =====================================================================
if __name__ == '__main__':
    # Security Fixes: 
    # - Run only on localhost (127.0.0.1) for secure, unexposed local development.
    # - Run with debug=False when not actively debugging to prevent arbitrary code execution.
    app.run(host='127.0.0.1', port=5000, debug=False)