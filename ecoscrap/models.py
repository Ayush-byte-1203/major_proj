"""
EcoScrap Application - Database Models
======================================

This module contains all the database models for the EcoScrap application.
It defines the structure and relationships between different data entities
using SQLAlchemy ORM.

Models Included:
- User: Authentication and user management
- Product: Marketplace items with approval workflow
- Transaction: Order and payment records
- Pickup: Scrap collection scheduling
- Rate: Current scrap material pricing
- Tip: Educational content for users

Database Relationships:
- Users can have multiple products (dealers)
- Users can have multiple transactions (customers/dealers)
- Users can have multiple pickups (customers)
- Products belong to dealers
- Transactions connect customers and dealers
- Rates are used for pickup value calculations

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

# Database instance (will be initialized in app.py)
db = SQLAlchemy()

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
    
    Security Features:
    - Password hashing with salt
    - Role-based access control
    - Account status management
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
        """
        Hash and set user password
        
        This method securely hashes the provided password using
        Werkzeug's generate_password_hash function, which includes
        salt for additional security.
        
        @param password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify user password
        
        This method compares the provided password with the stored
        hash using Werkzeug's check_password_hash function.
        
        @param password: Plain text password to verify
        @return: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        Convert user object to dictionary for JSON response
        
        This method serializes the user object for API responses,
        excluding sensitive information like password hashes.
        
        @return: Dictionary representation of user data
        """
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
        """
        Convert product object to dictionary for JSON response
        
        @return: Dictionary representation of product data
        """
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
        """
        Convert transaction object to dictionary for JSON response
        
        @return: Dictionary representation of transaction data
        """
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
        """
        Convert pickup object to dictionary for JSON response
        
        @return: Dictionary representation of pickup data
        """
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
        """
        Convert rate object to dictionary for JSON response
        
        @return: Dictionary representation of rate data
        """
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
        """
        Convert tip object to dictionary for JSON response
        
        @return: Dictionary representation of tip data
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'impact': self.impact
        }
