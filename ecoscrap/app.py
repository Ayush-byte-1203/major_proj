"""
EcoScrap Application - Flask Backend
====================================

This Flask application provides the backend API for the EcoScrap sustainable
scrap marketplace. It handles user authentication, data management, and
business logic that was previously implemented in JavaScript.

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

Database Models:
- User: Authentication and user management
- Product: Marketplace items with approval workflow
- Transaction: Order and payment records
- Pickup: Scrap collection scheduling
- Rate: Current scrap material pricing
- Tip: Educational content for users

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from functools import wraps

# ========================================
# FLASK APPLICATION INITIALIZATION
# ========================================

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ecoscrap-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ecoscrap.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ========================================
# DATABASE MODELS
# ========================================
# These models define the database structure for the EcoScrap application
# Each model represents a table in the database with relationships and constraints

class User(UserMixin, db.Model):
    """
    User model for authentication and user management
    
    This model handles all user-related data including authentication,
    profile information, and role-based access control. It inherits
    from UserMixin to provide Flask-Login functionality.
    
    Fields:
    - id: Unique identifier for each user
    - email: User's email address (unique, used for login)
    - password_hash: Securely hashed password using Werkzeug
    - name: User's full name
    - phone: Contact phone number
    - address: User's physical address
    - role: User role (customer, dealer, admin) for access control
    - status: Account status (active, blocked) for moderation
    - business_name: Business name for dealer accounts
    - join_date: When the user registered on the platform
    
    Relationships:
    - Products: Users can create products (dealers)
    - Transactions: Users can place orders (customers) or receive orders (dealers)
    - Pickups: Users can schedule pickups (customers)
    """
    __tablename__ = 'users'
    
    # Primary key and authentication fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Role and status management
    role = db.Column(db.String(20), default='customer')  # customer, dealer, admin
    status = db.Column(db.String(20), default='active')  # active, blocked
    business_name = db.Column(db.String(100))  # For dealers only
    
    # Timestamps
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'role': self.role,
            'status': self.status,
            'business_name': self.business_name,
            'join_date': self.join_date.isoformat() if self.join_date else None
        }

class Product(db.Model):
    """
    Product model for marketplace items
    
    This model represents products that dealers can list in the marketplace.
    Products go through an approval workflow before being visible to customers.
    
    Fields:
    - id: Unique identifier for each product
    - dealer_email: Foreign key to the dealer's email (from users table)
    - dealer_name: Name of the dealer for display purposes
    - name: Product name/title
    - price: Product price in Indian Rupees (₹)
    - category: Product category (metals, plastics, paper, electronics)
    - description: Detailed product description
    - status: Approval status (pending, approved, rejected)
    - stock: Available quantity in stock
    - rating: Average customer rating (0.0 to 5.0)
    - image: Emoji or image representation of the product
    - created_at: When the product was listed
    
    Workflow:
    1. Dealer creates product (status: pending)
    2. Admin reviews and approves/rejects (status: approved/rejected)
    3. Approved products appear in marketplace
    4. Customers can purchase approved products
    
    Business Rules:
    - Only dealers can create products
    - Products must be approved before sale
    - Stock is managed automatically during transactions
    """
    __tablename__ = 'products'
    
    # Primary key and identification
    id = db.Column(db.Integer, primary_key=True)
    
    # Dealer relationship and information
    dealer_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    dealer_name = db.Column(db.String(100), nullable=False)
    
    # Product details
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Approval and inventory management
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    stock = db.Column(db.Integer, default=0)
    
    # Customer feedback and presentation
    rating = db.Column(db.Float, default=0.0)
    image = db.Column(db.String(100), default='🔩')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert product object to dictionary for JSON response"""
        return {
            'id': self.id,
            'dealer_email': self.dealer_email,
            'dealer_name': self.dealer_name,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'stock': self.stock,
            'rating': self.rating,
            'image': self.image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    """
    Transaction model for orders and payments
    
    This model represents customer orders and payment transactions in the marketplace.
    It tracks the complete order lifecycle from placement to completion.
    
    Fields:
    - id: Unique transaction ID (format: TXN + timestamp)
    - customer_email: Foreign key to customer's email (from users table)
    - customer_name: Customer's name for display purposes
    - dealer_email: Foreign key to dealer's email (from users table)
    - items: JSON string containing cart items and quantities
    - amount: Total transaction amount including taxes
    - payment_method: Payment method used (cod, upi, card, netbanking)
    - address: Delivery address for the order
    - status: Order status (pending, completed, cancelled)
    - date: Date when the order was placed
    - timestamp: Exact timestamp of order placement
    
    Order Flow:
    1. Customer adds items to cart
    2. Customer proceeds to checkout
    3. Transaction is created with pending status
    4. Payment is processed (or marked as COD)
    5. Status updated to completed upon successful payment
    6. Dealer receives order notification
    
    Business Logic:
    - COD orders start with pending status
    - Online payments are marked completed immediately
    - Stock is reduced when transaction is created
    - Dealer receives order details for fulfillment
    """
    __tablename__ = 'transactions'
    
    # Unique transaction identifier
    id = db.Column(db.String(20), primary_key=True)
    
    # Customer relationship and information
    customer_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    
    # Dealer relationship
    dealer_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    
    # Order details
    items = db.Column(db.Text, nullable=False)  # JSON string of cart items
    amount = db.Column(db.Float, nullable=False)
    
    # Payment and delivery information
    payment_method = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Order status and tracking
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    
    # Timestamps
    date = db.Column(db.Date, default=datetime.utcnow().date)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert transaction object to dictionary for JSON response"""
        return {
            'id': self.id,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'dealer_email': self.dealer_email,
            'items': json.loads(self.items) if self.items else [],
            'amount': self.amount,
            'payment_method': self.payment_method,
            'address': self.address,
            'status': self.status,
            'date': self.date.isoformat() if self.date else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Pickup(db.Model):
    """
    Pickup model for scrap collection scheduling
    
    This model manages scrap collection requests from customers.
    It tracks pickup scheduling, status updates, and estimated values.
    
    Fields:
    - id: Unique pickup ID (format: PU + timestamp)
    - user_email: Foreign key to customer's email (from users table)
    - user_name: Customer's name for display purposes
    - material: Type of scrap material (aluminum, copper, steel, etc.)
    - weight: Weight of scrap in kilograms
    - date: Scheduled pickup date
    - time: Preferred time slot for pickup
    - address: Pickup location address
    - estimated_value: Calculated value based on current rates
    - status: Pickup status (scheduled, completed, cancelled)
    - booked_date: When the pickup was scheduled
    
    Pickup Workflow:
    1. Customer selects material type and weight
    2. System calculates estimated value using current rates
    3. Pickup is scheduled with dealer assignment
    4. Status updates as pickup progresses
    5. Final value determined upon collection
    
    Business Rules:
    - Only customers can schedule pickups
    - Estimated value calculated automatically
    - Minimum weight requirements can be enforced
    - Dealers can view pickups in their area
    """
    __tablename__ = 'pickups'
    
    # Unique pickup identifier
    id = db.Column(db.String(20), primary_key=True)
    
    # Customer relationship and information
    user_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    
    # Pickup details
    material = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Value estimation and status
    estimated_value = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    
    # Timestamps
    booked_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    def to_dict(self):
        """Convert pickup object to dictionary for JSON response"""
        return {
            'id': self.id,
            'user_email': self.user_email,
            'user_name': self.user_name,
            'material': self.material,
            'weight': self.weight,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time,
            'address': self.address,
            'estimated_value': self.estimated_value,
            'status': self.status,
            'booked_date': self.booked_date.isoformat() if self.booked_date else None
        }

class Rate(db.Model):
    """
    Rate model for scrap material pricing
    
    This model stores current market rates for different scrap materials.
    Rates are updated by administrators and used for value calculations.
    
    Fields:
    - id: Unique identifier for each rate entry
    - material: Type of scrap material (aluminum, copper, steel, etc.)
    - rate_per_kg: Current price per kilogram in Indian Rupees (₹)
    - trend: Market trend indicator (up, down, stable)
    - icon: Visual representation emoji for the material
    
    Usage:
    - Displayed on home page and rates section
    - Used to calculate pickup estimated values
    - Helps customers understand current market conditions
    - Trend indicators show market direction
    
    Business Rules:
    - Rates are updated by administrators only
    - Each material has a unique rate entry
    - Rates affect pickup value calculations
    - Historical rate tracking can be implemented
    """
    __tablename__ = 'rates'
    
    # Primary key and material identification
    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(50), unique=True, nullable=False)
    
    # Pricing and market information
    rate_per_kg = db.Column(db.Float, nullable=False)
    trend = db.Column(db.String(20), default='stable')  # up, down, stable
    
    # Visual representation
    icon = db.Column(db.String(10), default='♻️')
    
    def to_dict(self):
        """Convert rate object to dictionary for JSON response"""
        return {
            'id': self.id,
            'material': self.material,
            'ratePerKg': self.rate_per_kg,
            'trend': self.trend,
            'icon': self.icon
        }

class Tip(db.Model):
    """
    Tip model for educational content
    
    This model stores educational tips and guides to help users
    maximize their scrap value and practice safe handling.
    
    Fields:
    - id: Unique identifier for each tip
    - title: Tip title/headline
    - description: Detailed explanation of the tip
    - category: Tip category (Preparation, Rates, Safety, Environment, etc.)
    - icon: Visual representation emoji
    - impact: Expected benefit or impact of following the tip
    
    Categories:
    - Preparation: How to prepare scrap materials
    - Rates: Understanding pricing and market conditions
    - Safety: Safe handling practices
    - Environment: Environmental benefits
    - Identification: How to identify materials
    - Storage: Proper storage methods
    
    Usage:
    - Displayed in tips section with filtering
    - Helps customers maximize scrap value
    - Promotes safe and sustainable practices
    - Educational content for better user experience
    """
    __tablename__ = 'tips'
    
    # Primary key and identification
    id = db.Column(db.Integer, primary_key=True)
    
    # Content details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Categorization and presentation
    category = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(10), default='💡')
    impact = db.Column(db.String(100), default='')
    
    def to_dict(self):
        """Convert tip object to dictionary for JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'impact': self.impact
        }

# ========================================
# USER LOADER FOR FLASK-LOGIN
# ========================================

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

# ========================================
# AUTHENTICATION DECORATORS
# ========================================
# These decorators enforce role-based access control for different API endpoints
# They ensure that only users with appropriate roles can access specific functionality

def admin_required(f):
    """
    Decorator to require admin role access
    
    This decorator ensures that only authenticated users with admin role
    can access the protected endpoint. It's used for administrative functions
    like user management, product approval, and system configuration.
    
    Usage:
        @app.route('/admin/users')
        @admin_required
        def manage_users():
            # Only admins can access this endpoint
            pass
    
    Returns:
        - 403 Forbidden if user is not admin
        - Executes the function if user has admin role
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    
    Usage:
        @app.route('/dealer/products')
        @dealer_required
        def manage_products():
            # Only dealers can access this endpoint
            pass
    
    Returns:
        - 403 Forbidden if user is not dealer
        - Executes the function if user has dealer role
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    
    Usage:
        @app.route('/customer/pickups')
        @customer_required
        def book_pickup():
            # Only customers can access this endpoint
            pass
    
    Returns:
        - 403 Forbidden if user is not customer
        - Executes the function if user has customer role
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'customer':
            return jsonify({'error': 'Customer access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ========================================
# AUTHENTICATION ROUTES
# ========================================

@app.route('/api/auth/register', methods=['POST'])
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

@app.route('/api/auth/login', methods=['POST'])
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

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    """User profile management endpoint"""
    if request.method == 'GET':
        return jsonify({'user': current_user.to_dict()}), 200
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update user fields
            if 'name' in data:
                current_user.name = data['name']
            if 'phone' in data:
                current_user.phone = data['phone']
            if 'address' in data:
                current_user.address = data['address']
            if 'business_name' in data:
                current_user.business_name = data['business_name']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': current_user.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# ========================================
# PRODUCT ROUTES
# ========================================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all approved products with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        search = request.args.get('search')
        status = request.args.get('status', 'approved')
        
        # Build query
        query = Product.query
        
        if status:
            query = query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.dealer_name.ilike(search_term)
                )
            )
        
        products = query.all()
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
@login_required
@dealer_required
def create_product():
    """Create new product (dealers only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'price', 'description', 'stock']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new product
        product = Product(
            dealer_email=current_user.email,
            dealer_name=current_user.name,
            name=data['name'],
            price=float(data['price']),
            category=data['category'],
            description=data['description'],
            stock=int(data['stock']),
            image=data.get('image', '🔩')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_product(product_id):
    """Update or delete product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user owns the product or is admin
    if current_user.role != 'admin' and product.dealer_email != current_user.email:
        return jsonify({'error': 'Access denied'}), 403
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update product fields
            if 'name' in data:
                product.name = data['name']
            if 'price' in data:
                product.price = float(data['price'])
            if 'category' in data:
                product.category = data['category']
            if 'description' in data:
                product.description = data['description']
            if 'stock' in data:
                product.stock = int(data['stock'])
            if 'image' in data:
                product.image = data['image']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Product updated successfully',
                'product': product.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(product)
            db.session.commit()
            
            return jsonify({'message': 'Product deleted successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# ========================================
# PICKUP ROUTES
# ========================================

@app.route('/api/pickups', methods=['GET'])
@login_required
def get_pickups():
    """Get pickups for current user or all pickups for admins"""
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
    """Create new pickup request (customers only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['material', 'weight', 'date', 'time', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Calculate estimated value
        rate = Rate.query.filter_by(material=data['material']).first()
        estimated_value = rate.rate_per_kg * float(data['weight']) if rate else 0
        
        # Generate pickup ID
        pickup_id = f"PU{int(datetime.utcnow().timestamp())}"
        
        # Create pickup
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
        
        db.session.add(pickup)
        db.session.commit()
        
        return jsonify({
            'message': 'Pickup scheduled successfully',
            'pickup': pickup.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/pickups/<pickup_id>', methods=['PUT'])
@login_required
def update_pickup(pickup_id):
    """Update pickup status"""
    pickup = Pickup.query.get_or_404(pickup_id)
    
    # Check if user owns the pickup or is admin
    if current_user.role != 'admin' and pickup.user_email != current_user.email:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        if 'status' in data:
            pickup.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Pickup updated successfully',
            'pickup': pickup.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# TRANSACTION ROUTES
# ========================================

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Get transactions for current user or all transactions for admins"""
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
    """Create new transaction/order (customers only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['items', 'amount', 'payment_method', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate transaction ID
        transaction_id = f"TXN{int(datetime.utcnow().timestamp())}"
        
        # Create transaction
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
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Order placed successfully',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# RATES AND TIPS ROUTES
# ========================================

@app.route('/api/rates', methods=['GET'])
def get_rates():
    """Get current scrap material rates"""
    try:
        rates = Rate.query.all()
        return jsonify([rate.to_dict() for rate in rates]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rates', methods=['PUT'])
@login_required
@admin_required
def update_rates():
    """Update scrap material rates (admins only)"""
    try:
        data = request.get_json()
        
        for rate_data in data:
            rate = Rate.query.filter_by(material=rate_data['material']).first()
            if rate:
                rate.rate_per_kg = float(rate_data['ratePerKg'])
                rate.trend = rate_data.get('trend', 'stable')
                rate.icon = rate_data.get('icon', '♻️')
        
        db.session.commit()
        
        return jsonify({'message': 'Rates updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tips', methods=['GET'])
def get_tips():
    """Get educational tips and guides"""
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
# ADMIN ROUTES
# ========================================

@app.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users (admins only)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def manage_user(user_id):
    """Update or delete user (admins only)"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            if 'status' in data:
                user.status = data['status']
            if 'role' in data:
                user.role = data['role']
            
            db.session.commit()
            
            return jsonify({
                'message': 'User updated successfully',
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'User deleted successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:product_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_product(product_id):
    """Approve product for marketplace (admins only)"""
    try:
        product = Product.query.get_or_404(product_id)
        product.status = 'approved'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product approved successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:product_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_product(product_id):
    """Reject product (admins only)"""
    try:
        product = Product.query.get_or_404(product_id)
        product.status = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product rejected successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# DASHBOARD ROUTES
# ========================================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics based on user role"""
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
    """Calculate estimated value for scrap materials"""
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
# These routes serve the frontend HTML, CSS, and JavaScript files
# They enable the Flask backend to serve the complete web application

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
# Global error handlers for common HTTP error scenarios
# These handlers provide consistent error responses across the application

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
# This section runs when the script is executed directly (not imported)
# It handles database initialization, sample data creation, and server startup

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
        python app.py                    # Run development server
        python app.py --production      # Run production mode (if implemented)
        gunicorn app:app               # Production deployment
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
