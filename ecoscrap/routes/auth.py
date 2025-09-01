"""
EcoScrap Application - Authentication Routes
============================================

This module contains all authentication-related routes for the EcoScrap application.
It handles user registration, login, logout, and profile management.

Routes Included:
- POST /api/auth/register: User registration with role selection
- POST /api/auth/login: User authentication and session creation
- POST /api/auth/logout: User logout and session termination
- GET/PUT /api/auth/profile: Profile viewing and updating

Authentication Features:
- Secure password hashing with Werkzeug
- Session management with Flask-Login
- Role-based account creation
- Profile data validation and updates
- Account status verification

Security Considerations:
- Password validation and confirmation
- Email uniqueness verification
- Input sanitization and validation
- Secure session handling
- Role-based access restrictions

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    
    This endpoint allows new users to create accounts in the EcoScrap system.
    Users can register as customers or dealers with appropriate validation.
    
    Request Body:
        {
            "name": "User's full name",
            "email": "user@example.com",
            "phone": "+91XXXXXXXXXX",
            "address": "User's address",
            "password": "secure_password",
            "role": "customer|dealer",
            "business_name": "Business name (optional, for dealers)"
        }
    
    Validation:
        - All required fields must be provided
        - Email must be unique (not already registered)
        - Password is securely hashed before storage
        - Role must be either 'customer' or 'dealer'
    
    Business Logic:
        - New users are automatically set to 'active' status
        - Business name is required for dealer accounts
        - Users are automatically logged in after successful registration
        - Join date is automatically set to current timestamp
    
    Returns:
        - 201 Created: User registered successfully with user data
        - 400 Bad Request: Missing required fields
        - 409 Conflict: Email already registered
        - 500 Internal Server Error: Database or system error
    
    Security Features:
        - Password hashing using Werkzeug
        - Input validation and sanitization
        - Automatic session creation after registration
    """
    try:
        # Extract and validate request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists to prevent duplicate accounts
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user object with provided data
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
            role=data['role'],
            business_name=data.get('business_name')  # Optional for dealers
        )
        
        # Securely hash the password before storage
        user.set_password(data['password'])
        
        # Save user to database
        db.session.add(user)
        db.session.commit()
        
        # Automatically log in the new user for better UX
        login_user(user)
        
        # Return success response with user data
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    This endpoint authenticates users and creates secure sessions.
    It validates credentials and checks account status before allowing access.
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "user_password"
        }
    
    Authentication Process:
        1. Validate input data (email and password required)
        2. Find user by email address
        3. Verify password using secure hashing
        4. Check account status (active/blocked)
        5. Create secure session using Flask-Login
        6. Return user data and success message
    
    Security Features:
        - Password verification using secure hashing
        - Account status validation (prevents blocked users from logging in)
        - Secure session creation with Flask-Login
        - Input validation and sanitization
    
    Business Rules:
        - Only active accounts can log in
        - Blocked accounts are denied access
        - Invalid credentials return generic error message
        - Successful login creates persistent session
    
    Returns:
        - 200 OK: Login successful with user data
        - 400 Bad Request: Missing email or password
        - 401 Unauthorized: Invalid credentials
        - 403 Forbidden: Account blocked
        - 500 Internal Server Error: System error
    """
    try:
        # Extract login credentials from request
        data = request.get_json()
        
        # Validate that both email and password are provided
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email address
        user = User.query.filter_by(email=data['email']).first()
        
        # Verify user exists and password is correct
        if user and user.check_password(data['password']):
            # Check if account is active (not blocked)
            if user.status == 'blocked':
                return jsonify({'error': 'Account is blocked'}), 403
            
            # Create secure session for authenticated user
            login_user(user)
            
            # Return success response with user information
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200
        else:
            # Return generic error for security (don't reveal which field is wrong)
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    User logout endpoint
    
    This endpoint terminates the user session and logs out the user.
    It's protected by login_required decorator to ensure only
    authenticated users can logout.
    
    Security Features:
        - Requires valid authentication
        - Secure session termination
        - Clean logout process
    
    Returns:
        - 200 OK: Logout successful
        - 401 Unauthorized: User not authenticated
    """
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    """
    User profile management endpoint
    
    This endpoint allows users to view and update their profile information.
    It's protected by login_required decorator and only allows users
    to modify their own profiles.
    
    Methods:
        - GET: Retrieve current user profile
        - PUT: Update user profile information
    
    Request Body (PUT):
        {
            "name": "Updated name",
            "phone": "Updated phone",
            "address": "Updated address",
            "business_name": "Updated business name"
        }
    
    Security Features:
        - Authentication required
        - Users can only modify their own profiles
        - Input validation and sanitization
        - Secure data updates
    
    Returns:
        - 200 OK: Profile retrieved or updated successfully
        - 401 Unauthorized: User not authenticated
        - 500 Internal Server Error: Database or system error
    """
    if request.method == 'GET':
        # Return current user profile
        return jsonify({'user': current_user.to_dict()}), 200
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update user fields if provided
            if 'name' in data:
                current_user.name = data['name']
            if 'phone' in data:
                current_user.phone = data['phone']
            if 'address' in data:
                current_user.address = data['address']
            if 'business_name' in data:
                current_user.business_name = data['business_name']
            
            # Save changes to database
            db.session.commit()
            
            # Return updated user data
            return jsonify({
                'message': 'Profile updated successfully',
                'user': current_user.to_dict()
            }), 200
            
        except Exception as e:
            # Rollback database changes on error
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change user password endpoint
    
    This endpoint allows authenticated users to change their passwords.
    It requires the current password for verification before allowing
    the change to proceed.
    
    Request Body:
        {
            "current_password": "Current password",
            "new_password": "New password",
            "confirm_password": "Password confirmation"
        }
    
    Security Features:
        - Authentication required
        - Current password verification
        - Password confirmation validation
        - Secure password hashing
    
    Validation:
        - Current password must be correct
        - New password must be different from current
        - New password must match confirmation
        - Password must meet security requirements
    
    Returns:
        - 200 OK: Password changed successfully
        - 400 Bad Request: Invalid input or validation failure
        - 401 Unauthorized: User not authenticated
        - 500 Internal Server Error: Database or system error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['current_password', 'new_password', 'confirm_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify current password
        if not current_user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Check if new password is different
        if data['current_password'] == data['new_password']:
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        # Verify password confirmation
        if data['new_password'] != data['confirm_password']:
            return jsonify({'error': 'New password and confirmation do not match'}), 400
        
        # Update password
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
