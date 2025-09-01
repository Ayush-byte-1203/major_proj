"""
EcoScrap Application - Modular Flask Backend
============================================

This is the main Flask application file that imports and uses modular components
for better code organization and maintainability. The application is structured
into separate modules for different functionality areas.

Module Structure:
- models.py: Database models and ORM definitions
- decorators.py: Role-based access control decorators
- routes/auth.py: Authentication and user management routes
- routes/products.py: Product and marketplace routes
- routes/pickups.py: Pickup scheduling routes
- routes/transactions.py: Order and transaction routes
- routes/admin.py: Administrative functions routes
- routes/dashboard.py: Dashboard and analytics routes

Key Features:
- User authentication and authorization with Flask-Login
- Product management and marketplace operations with approval workflow
- Pickup scheduling and management for scrap collection
- Order processing and transactions with payment methods
- Admin dashboard and user management with role-based access
- RESTful API endpoints for frontend integration
- SQLite database with SQLAlchemy ORM
- Session management and security features

Architecture:
- Flask web framework with modular structure
- SQLAlchemy ORM for database operations
- Flask-Login for user authentication
- Role-based access control (Customer, Dealer, Admin)
- RESTful API design with JSON responses
- Error handling and validation

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

from flask import Flask, request, jsonify, session, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import json

# Import modular components
from models import db, User, Product, Rate, Tip, Transaction, Pickup
from decorators import admin_required, dealer_required, customer_required
from routes.auth import auth_bp
from routes.products import products_bp

# ========================================
# FLASK APPLICATION INITIALIZATION
# ========================================

def create_app():
    """
    Application factory function
    
    This function creates and configures the Flask application instance.
    It sets up all extensions, blueprints, and configuration options.
    
    Configuration:
        - Secret key for session security
        - Database connection and settings
        - Flask-Login configuration
        - Blueprint registration
    
    Returns:
        Flask application instance
    """
    # Create Flask application instance
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # Configure application settings
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ecoscrap-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ecoscrap.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with application context
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Register blueprints for modular routing
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    
    # Register additional blueprints (to be implemented)
    # app.register_blueprint(pickups_bp)
    # app.register_blueprint(transactions_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(dashboard_bp)
    
    return app

# Create application instance
app = create_app()

# ========================================
# PICKUP ROUTES (Temporary - will be moved to routes/pickups.py)
# ========================================

@app.route('/api/pickups', methods=['GET'])
@login_required
def get_pickups():
    """
    Get pickups for current user or all pickups for admins
    
    This endpoint retrieves pickup requests based on user role and permissions.
    
    Business Logic:
        - Admins see all pickups in the system
        - Dealers see pickups in their area (could be enhanced with location)
        - Customers see only their own pickups
    
    Security Features:
        - Authentication required
        - Role-based data access
        - User data isolation
    
    Returns:
        - 200 OK: List of pickups matching user permissions
        - 401 Unauthorized: User not authenticated
        - 500 Internal Server Error: Database or system error
    """
    try:
        if current_user.role == 'admin':
            pickups = Pickup.query.all()
        elif current_user.role == 'dealer':
            # Dealers see pickups in their area (could be enhanced with location)
            pickups = Pickup.query.all()
        else:
            # Customers see only their own pickups
            pickups = Pickup.query.filter_by(user_email=current_user.email).all()
        
        return jsonify([pickup.to_dict() for pickup in pickups]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pickups', methods=['POST'])
@login_required
@customer_required
def create_pickup():
    """
    Create new pickup request (customers only)
    
    This endpoint allows customers to schedule scrap collection pickups.
    The system automatically calculates estimated value based on current rates.
    
    Request Body:
        {
            "material": "aluminum",
            "weight": 25.5,
            "date": "2024-01-15",
            "time": "10:00 AM",
            "address": "Pickup address"
        }
    
    Business Logic:
        - Only customers can schedule pickups
        - Estimated value calculated automatically using current rates
        - Unique pickup ID generated with timestamp
        - Pickup scheduled with 'scheduled' status
    
    Validation:
        - All required fields must be provided
        - Weight must be positive number
        - Date must be valid format
        - Material must exist in rates table
    
    Returns:
        - 201 Created: Pickup scheduled successfully
        - 400 Bad Request: Missing required fields or validation failure
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not a customer
        - 500 Internal Server Error: Database or system error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['material', 'weight', 'date', 'time', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Calculate estimated value using current rates
        rate = Rate.query.filter_by(material=data['material']).first()
        estimated_value = rate.rate_per_kg * float(data['weight']) if rate else 0
        
        # Generate unique pickup ID
        pickup_id = f"PU{int(datetime.utcnow().timestamp())}"
        
        # Create pickup request
        pickup = Pickup(
            id=pickup_id,
            user_email=current_user.email,
            user_name=current_user.name,
            material=data['material'],
            weight=float(data['weight']),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            time=data['time'],
            address=data['address'],
            estimated_value=estimated_value
        )
        
        # Save pickup to database
        db.session.add(pickup)
        db.session.commit()
        
        # Return success response with pickup data
        return jsonify({
            'message': 'Pickup scheduled successfully',
            'pickup': pickup.to_dict()
        }), 201
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# TRANSACTION ROUTES (Temporary - will be moved to routes/transactions.py)
# ========================================

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    """
    Get transactions for current user or all transactions for admins
    
    This endpoint retrieves transaction history based on user role and permissions.
    
    Business Logic:
        - Admins see all transactions in the system
        - Dealers see transactions where they are the seller
        - Customers see transactions where they are the buyer
    
    Security Features:
        - Authentication required
        - Role-based data access
        - User data isolation
    
    Returns:
        - 200 OK: List of transactions matching user permissions
        - 401 Unauthorized: User not authenticated
        - 500 Internal Server Error: Database or system error
    """
    try:
        if current_user.role == 'admin':
            transactions = Transaction.query.all()
        elif current_user.role == 'dealer':
            transactions = Transaction.query.filter_by(dealer_email=current_user.email).all()
        else:
            transactions = Transaction.query.filter_by(customer_email=current_user.email).all()
        
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
@login_required
@customer_required
def create_transaction():
    """
    Create new transaction/order (customers only)
    
    This endpoint allows customers to place orders and create transactions.
    The system handles order processing and status management.
    
    Request Body:
        {
            "items": [{"product_id": 1, "quantity": 2}],
            "amount": 250.00,
            "payment_method": "cod",
            "address": "Delivery address"
        }
    
    Business Logic:
        - Only customers can create transactions
        - Transaction ID generated with timestamp
        - Status set based on payment method
        - COD orders start with 'pending' status
        - Online payments marked as 'completed'
    
    Validation:
        - All required fields must be provided
        - Amount must be positive number
        - Payment method must be valid
        - Items must be valid product references
    
    Returns:
        - 201 Created: Order placed successfully
        - 400 Bad Request: Missing required fields or validation failure
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not a customer
        - 500 Internal Server Error: Database or system error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['items', 'amount', 'payment_method', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate unique transaction ID
        transaction_id = f"TXN{int(datetime.utcnow().timestamp())}"
        
        # Create transaction record
        transaction = Transaction(
            id=transaction_id,
            customer_email=current_user.email,
            customer_name=current_user.name,
            dealer_email=data['dealer_email'],
            items=json.dumps(data['items']),
            amount=float(data['amount']),
            payment_method=data['payment_method'],
            address=data['address'],
            status='pending' if data['payment_method'] == 'cod' else 'completed'
        )
        
        # Save transaction to database
        db.session.add(transaction)
        db.session.commit()
        
        # Return success response with transaction data
        return jsonify({
            'message': 'Order placed successfully',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# RATES AND TIPS ROUTES (Temporary - will be moved to routes/content.py)
# ========================================

@app.route('/api/rates', methods=['GET'])
def get_rates():
    """
    Get current scrap material rates
    
    This endpoint provides current market rates for different scrap materials.
    It's accessible to all users without authentication.
    
    Business Logic:
        - Returns all available material rates
        - Includes trend indicators and icons
        - Used for pickup value calculations
        - Helps customers understand market conditions
    
    Returns:
        - 200 OK: List of current material rates
        - 500 Internal Server Error: Database or system error
    """
    try:
        rates = Rate.query.all()
        return jsonify([rate.to_dict() for rate in rates]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tips', methods=['GET'])
def get_tips():
    """
    Get educational tips and guides
    
    This endpoint provides educational content to help users maximize
    their scrap value and practice safe handling.
    
    Query Parameters:
        - category: Filter tips by category
    
    Business Logic:
        - Returns educational tips and guides
        - Optional category filtering
        - Helps users understand best practices
        - Promotes safe and sustainable practices
    
    Returns:
        - 200 OK: List of educational tips
        - 500 Internal Server Error: Database or system error
    """
    try:
        category = request.args.get('category')
        
        query = Tip.query
        if category:
            query = query.filter_by(category=category)
        
        tips = query.all()
        return jsonify([tip.to_dict() for tip in tips]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================
# ADMIN ROUTES (Temporary - will be moved to routes/admin.py)
# ========================================

@app.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """
    Get all users (admins only)
    
    This endpoint provides administrators with access to all user accounts
    in the system for management and moderation purposes.
    
    Security Features:
        - Admin-only access
        - Full user list visibility
        - Sensitive data included (for admin use)
    
    Returns:
        - 200 OK: List of all users in the system
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not admin
        - 500 Internal Server Error: Database or system error
    """
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================
# DASHBOARD ROUTES (Temporary - will be moved to routes/dashboard.py)
# ========================================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """
    Get dashboard statistics based on user role
    
    This endpoint provides role-specific dashboard statistics and analytics.
    Different user roles see different metrics relevant to their needs.
    
    Business Logic:
        - Admins see system-wide statistics
        - Dealers see business-specific metrics
        - Customers see personal usage statistics
    
    Admin Statistics:
        - Total users, products, revenue, pickup requests
    
    Dealer Statistics:
        - Total products, earnings, pending approvals, orders received
    
    Customer Statistics:
        - Total pickups, orders, amount spent
    
    Returns:
        - 200 OK: Role-specific dashboard statistics
        - 401 Unauthorized: User not authenticated
        - 500 Internal Server Error: Database or system error
    """
    try:
        if current_user.role == 'admin':
            # Admin dashboard stats
            stats = {
                'total_users': User.query.count(),
                'total_products': Product.query.count(),
                'total_revenue': db.session.query(db.func.sum(Transaction.amount)).scalar() or 0,
                'pickup_requests': Pickup.query.count()
            }
        elif current_user.role == 'dealer':
            # Dealer dashboard stats
            products = Product.query.filter_by(dealer_email=current_user.email).all()
            transactions = Transaction.query.filter_by(dealer_email=current_user.email).all()
            
            stats = {
                'total_products': len(products),
                'total_earnings': sum(t.amount for t in transactions),
                'pending_approval': len([p for p in products if p.status == 'pending']),
                'orders_received': len(transactions)
            }
        else:
            # Customer dashboard stats
            pickups = Pickup.query.filter_by(user_email=current_user.email).all()
            transactions = Transaction.query.filter_by(customer_email=current_user.email).all()
            
            stats = {
                'total_pickups': len(pickups),
                'total_orders': len(transactions),
                'total_spent': sum(t.amount for t in transactions)
            }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================
# UTILITY ROUTES
# ========================================

@app.route('/api/calculate-estimate', methods=['POST'])
def calculate_estimate():
    """
    Calculate estimated value for scrap materials
    
    This endpoint calculates the estimated value of scrap materials
    based on current market rates and weight.
    
    Request Body:
        {
            "material": "aluminum",
            "weight": 25.5
        }
    
    Business Logic:
        - Uses current market rates for calculation
        - Calculates value as rate_per_kg × weight
        - Provides real-time pricing information
        - Helps customers estimate pickup value
    
    Validation:
        - Material must exist in rates table
        - Weight must be positive number
    
    Returns:
        - 200 OK: Estimated value calculation
        - 400 Bad Request: Missing required fields or validation failure
        - 404 Not Found: Material rate not found
        - 500 Internal Server Error: System error
    """
    try:
        data = request.get_json()
        material = data.get('material')
        weight = float(data.get('weight', 0))
        
        if not material or weight <= 0:
            return jsonify({'error': 'Material and weight are required'}), 400
        
        rate = Rate.query.filter_by(material=material).first()
        if not rate:
            return jsonify({'error': 'Material rate not found'}), 404
        
        estimated_value = rate.rate_per_kg * weight
        
        return jsonify({
            'estimated_value': estimated_value,
            'rate_per_kg': rate.rate_per_kg,
            'weight': weight
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================
# FRONTEND ROUTES
# ========================================

@app.route('/')
def index():
    """
    Serve the main HTML frontend
    
    This route serves the index.html file which contains the main
    EcoScrap application interface. It's the entry point for users
    accessing the website.
    
    Frontend Features:
        - Hero section with pickup booking
        - Marketplace product browsing
        - Current rates display
        - Tips and educational content
        - User authentication interface
        - Role-based dashboard access
    
    Returns:
        - index.html: Main application HTML file
        - 404: If index.html is not found
    """
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """
    Serve static files (CSS, JS, images)
    
    This catch-all route serves all static assets needed by the frontend,
    including CSS stylesheets, JavaScript modules, and image files.
    
    Supported File Types:
        - CSS: Stylesheets for layout and components
        - JavaScript: Application logic and modules
        - Images: Icons, logos, and visual assets
        - Fonts: Custom typography files
    
    File Organization:
        - /css/: Stylesheets (main.css, layout.css, components.css)
        - /js/: JavaScript modules (api-client.js, modules/*.js)
        - /images/: Visual assets and icons
    
    Security:
        - Only serves files from the configured static folder
        - Prevents directory traversal attacks
        - Validates file paths before serving
    
    @param filename: Path to the requested static file
    @returns: Requested static file or 404 if not found
    """
    return app.send_static_file(filename)

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors
    
    This handler catches all requests to non-existent routes and resources.
    It provides a consistent JSON error response for API endpoints and
    falls back to serving the main application for frontend routes.
    
    Error Scenarios:
        - Invalid API endpoints
        - Missing static files
        - Non-existent database records
        - Malformed URLs
    
    Response Format:
        - JSON error message for API requests
        - Appropriate HTTP status code
        - Consistent error structure
    
    @param error: The 404 error object from Flask
    @returns: JSON error response with 404 status
    """
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors
    
    This handler catches all unhandled exceptions and server errors.
    It ensures database consistency by rolling back any pending
    transactions and provides a safe error response.
    
    Error Scenarios:
        - Unhandled exceptions in route handlers
        - Database connection failures
        - Server configuration issues
        - Unexpected runtime errors
    
    Safety Features:
        - Automatic database rollback on errors
        - Prevents partial transaction commits
        - Maintains data integrity
        - Logs error details for debugging
    
    Response Format:
        - Generic error message (no sensitive information)
        - 500 Internal Server Error status
        - Database state is safely restored
    
    @param error: The 500 error object from Flask
    @returns: JSON error response with 500 status
    """
    # Rollback any pending database transactions to maintain consistency
    db.session.rollback()
    
    # Return generic error message (don't expose internal details)
    return jsonify({'error': 'Internal server error'}), 500

# ========================================
# APPLICATION ENTRY POINT
# ========================================

if __name__ == '__main__':
    """
    Main application entry point
    
    This block runs when the script is executed directly (not imported).
    It initializes the database and starts the Flask development server.
    
    Startup Process:
        1. Create application context for database operations
        2. Initialize database tables if they don't exist
        3. Populate sample data for demonstration
        4. Start Flask development server with specified configuration
    
    Database Initialization:
        - Creates all tables defined in SQLAlchemy models
        - Populates sample rates for scrap materials
        - Adds educational tips for users
        - Ensures application is ready for immediate use
    
    Server Configuration:
        - Debug mode: Enabled for development (auto-reload, detailed errors)
        - Host: 0.0.0.0 (accessible from any network interface)
        - Port: 5001 (avoiding conflicts with other services)
    
    Development Features:
        - Auto-reload on code changes
        - Detailed error messages and stack traces
        - Interactive debugger for troubleshooting
        - Hot reloading of templates and static files
    
    Production Notes:
        - Debug mode should be disabled in production
        - Use gunicorn or uwsgi for production deployment
        - Configure proper logging and monitoring
        - Set appropriate security headers
    
    Usage:
        python app_modular.py                    # Run development server
        python app_modular.py --production      # Run production mode (if implemented)
        gunicorn app_modular:app               # Production deployment
    """
    # Create application context for database operations
    with app.app_context():
        # Create database tables if they don't exist
        # This ensures the database schema is ready before serving requests
        db.create_all()
        
        # Initialize sample data if database is empty
        # This provides demonstration data for immediate testing
        if not Rate.query.first():
            # Sample scrap material rates with realistic Indian pricing
            # Rates are based on current market conditions and trends
            sample_rates = [
                {'material': 'Aluminum', 'rate_per_kg': 140, 'trend': 'up', 'icon': '🥤'},
                {'material': 'Copper', 'rate_per_kg': 650, 'trend': 'up', 'icon': '🔌'},
                {'material': 'Steel', 'rate_per_kg': 45, 'trend': 'stable', 'icon': '🔩'},
                {'material': 'Brass', 'rate_per_kg': 420, 'trend': 'up', 'icon': '🔧'},
                {'material': 'Iron', 'rate_per_kg': 35, 'trend': 'stable', 'icon': '⚙️'},
                {'material': 'Plastic', 'rate_per_kg': 25, 'trend': 'down', 'icon': '♻️'},
                {'material': 'Cardboard', 'rate_per_kg': 8, 'trend': 'up', 'icon': '📦'},
                {'material': 'Newspaper', 'rate_per_kg': 12, 'trend': 'stable', 'icon': '📰'},
                {'material': 'Electronics', 'rate_per_kg': 250, 'trend': 'up', 'icon': '💾'}
            ]
            
            # Add each rate to the database
            for rate_data in sample_rates:
                rate = Rate(**rate_data)
                db.session.add(rate)
            
            # Commit all rates to database
            db.session.commit()
        
        # Initialize sample tips if database is empty
        if not Tip.query.first():
            # Sample educational tips for users to maximize scrap value
            # These tips help users understand best practices
            sample_tips = [
                {
                    'title': 'Clean Your Metals Before Pickup',
                    'description': 'Remove dirt, paint, and non-metal attachments from steel, aluminum, and copper to get better rates. Clean metals fetch 15-20% higher prices.',
                    'category': 'Preparation',
                    'icon': '🧽',
                    'impact': 'Higher Rates'
                },
                {
                    'title': 'Separate Different Metal Types',
                    'description': 'Don\'t mix aluminum with steel or copper. Different metals have different values. Copper is most valuable, then aluminum, then steel.',
                    'category': 'Rates',
                    'icon': '🔧',
                    'impact': 'Better Pricing'
                }
            ]
            
            # Add each tip to the database
            for tip_data in sample_tips:
                tip = Tip(**tip_data)
                db.session.add(tip)
            
            # Commit all tips to database
            db.session.commit()
    
    # Start the Flask development server
    app.run(
        debug=True,           # Enable debug mode for development
        host='0.0.0.0',      # Bind to all network interfaces
        port=5001            # Use port 5001 to avoid conflicts
    )
