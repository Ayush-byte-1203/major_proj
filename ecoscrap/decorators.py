"""
EcoScrap Application - Access Control Decorators
================================================

This module contains decorators for implementing role-based access control (RBAC)
in the EcoScrap application. These decorators ensure that only users with
appropriate roles can access specific functionality.

Decorators Included:
- admin_required: Restricts access to admin users only
- dealer_required: Restricts access to dealer users only
- customer_required: Restricts access to customer users only

Security Features:
- Role verification before function execution
- Automatic access denial for unauthorized users
- Consistent error responses for security
- Integration with Flask-Login authentication

Usage Examples:
    @app.route('/admin/users')
    @admin_required
    def manage_users():
        # Only admins can access this endpoint
        pass

    @app.route('/dealer/products')
    @dealer_required
    def manage_products():
        # Only dealers can access this endpoint
        pass

    @app.route('/customer/pickups')
    @customer_required
    def book_pickup():
        # Only customers can access this endpoint
        pass

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

from functools import wraps
from flask import jsonify
from flask_login import current_user

def admin_required(f):
    """
    Decorator to require admin role access
    
    This decorator ensures that only authenticated users with admin role
    can access the protected endpoint. It's used for administrative functions
    like user management, product approval, and system configuration.
    
    Security Features:
    - Verifies user authentication status
    - Checks user role is 'admin'
    - Returns 403 Forbidden for unauthorized access
    - Maintains function signature and return values
    
    Usage:
        @app.route('/admin/users')
        @admin_required
        def manage_users():
            # Only admins can access this endpoint
            pass
    
    @param f: The function to decorate
    @return: Decorated function with access control
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has admin role
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def dealer_required(f):
    """
    Decorator to require dealer role access
    
    This decorator ensures that only authenticated users with dealer role
    can access the protected endpoint. It's used for dealer-specific functions
    like product management, order viewing, and business operations.
    
    Security Features:
    - Verifies user authentication status
    - Checks user role is 'dealer'
    - Returns 403 Forbidden for unauthorized access
    - Maintains function signature and return values
    
    Usage:
        @app.route('/dealer/products')
        @dealer_required
        def manage_products():
            # Only dealers can access this endpoint
            pass
    
    @param f: The function to decorate
    @return: Decorated function with access control
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has dealer role
        if not current_user.is_authenticated or current_user.role != 'dealer':
            return jsonify({'error': 'Dealer access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """
    Decorator to require customer role access
    
    This decorator ensures that only authenticated users with customer role
    can access the protected endpoint. It's used for customer-specific functions
    like placing orders, booking pickups, and viewing personal data.
    
    Security Features:
    - Verifies user authentication status
    - Checks user role is 'customer'
    - Returns 403 Forbidden for unauthorized access
    - Maintains function signature and return values
    
    Usage:
        @app.route('/customer/pickups')
        @customer_required
        def book_pickup():
            # Only customers can access this endpoint
            pass
    
    @param f: The function to decorate
    @return: Decorated function with access control
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has customer role
        if not current_user.is_authenticated or current_user.role != 'customer':
            return jsonify({'error': 'Customer access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """
    Flexible decorator for role-based access control
    
    This decorator allows specifying multiple allowed roles for an endpoint.
    It's useful for endpoints that should be accessible by multiple user types
    but not by all users.
    
    Security Features:
    - Verifies user authentication status
    - Checks user role is in allowed roles list
    - Returns 403 Forbidden for unauthorized access
    - Maintains function signature and return values
    
    Usage:
        @app.route('/profile')
        @role_required(['customer', 'dealer', 'admin'])
        def view_profile():
            # All authenticated users can access this endpoint
            pass
    
    @param allowed_roles: List of roles allowed to access the endpoint
    @return: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated and has an allowed role
            if not current_user.is_authenticated or current_user.role not in allowed_roles:
                return jsonify({'error': f'Access restricted to: {", ".join(allowed_roles)}'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def active_user_required(f):
    """
    Decorator to require active user account
    
    This decorator ensures that only users with active accounts can access
    the protected endpoint. It's useful for preventing blocked users from
    accessing any functionality.
    
    Security Features:
    - Verifies user authentication status
    - Checks user account status is 'active'
    - Returns 403 Forbidden for blocked accounts
    - Maintains function signature and return values
    
    Usage:
        @app.route('/api/data')
        @active_user_required
        def get_data():
            # Only active users can access this endpoint
            pass
    
    @param f: The function to decorate
    @return: Decorated function with access control
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has active status
        if not current_user.is_authenticated or current_user.status != 'active':
            return jsonify({'error': 'Active account required'}), 403
        return f(*args, **kwargs)
    return decorated_function
