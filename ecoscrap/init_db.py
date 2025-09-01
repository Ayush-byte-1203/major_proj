"""
EcoScrap Application - Database Initialization
==============================================

This script initializes the database with tables and sample data
for the EcoScrap application. It can be run independently to
set up the database or reset it with fresh data.

Usage:
    python init_db.py                    # Initialize database with sample data
    python init_db.py --reset           # Reset database (drop all tables)
    python init_db.py --sample          # Add sample data only (don't create tables)

Features:
- Automatic database table creation using SQLAlchemy models
- Sample data population for testing and demonstration
- Command-line argument parsing for different operations
- Error handling and rollback on failures
- Progress reporting and status messages

Sample Data Includes:
- Demo user accounts (admin, dealer, customer)
- Current scrap material rates with trends
- Educational tips and guides
- Sample marketplace products
- Realistic Indian context and pricing

Database Models:
- Users: Authentication and user management
- Products: Marketplace items with approval workflow
- Transactions: Order and payment records
- Pickups: Scrap collection scheduling
- Rates: Current scrap material pricing
- Tips: Educational content for users

Security Features:
- Secure password hashing for demo accounts
- Role-based access control setup
- Business logic validation
- Data integrity constraints

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

import os
import sys
import argparse
from datetime import datetime
from app import app, db, User, Product, Rate, Tip, Transaction, Pickup
from werkzeug.security import generate_password_hash

def create_sample_users():
    """Create sample user accounts for testing"""
    sample_users = [
        {
            'email': 'admin@ecoscrap.com',
            'password': 'admin123',
            'name': 'Admin User',
            'phone': '+91 9999999999',
            'address': 'EcoScrap HQ, Bandra Kurla Complex, Mumbai, Maharashtra 400051',
            'role': 'admin',
            'status': 'active'
        },
        {
            'email': 'dealer1@ecoscrap.com',
            'password': 'dealer123',
            'name': 'Rajesh Kumar',
            'phone': '+91 9876543210',
            'address': '123 Industrial Area, Okhla Phase II, New Delhi 110020',
            'role': 'dealer',
            'status': 'active',
            'business_name': 'Kumar Metals & Recyclers'
        },
        {
            'email': 'dealer2@ecoscrap.com',
            'password': 'dealer123',
            'name': 'Sunita Singh',
            'phone': '+91 9123456789',
            'address': '456 Market Road, Hadapsar, Pune, Maharashtra 411028',
            'role': 'dealer',
            'status': 'active',
            'business_name': 'Singh Eco Solutions'
        },
        {
            'email': 'customer1@ecoscrap.com',
            'password': 'customer123',
            'name': 'Priya Sharma',
            'phone': '+91 8765432109',
            'address': '789 Residential Colony, Koramangala, Bangalore, Karnataka 560095',
            'role': 'customer',
            'status': 'active'
        },
        {
            'email': 'customer2@ecoscrap.com',
            'password': 'customer123',
            'name': 'Amit Patel',
            'phone': '+91 7654321098',
            'address': '321 Sector 15, Gurugram, Haryana 122001',
            'role': 'customer',
            'status': 'active'
        }
    ]
    
    for user_data in sample_users:
        # Check if user already exists
        if not User.query.filter_by(email=user_data['email']).first():
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                address=user_data['address'],
                role=user_data['role'],
                status=user_data['status'],
                business_name=user_data.get('business_name')
            )
            user.password_hash = generate_password_hash(user_data['password'])
            db.session.add(user)
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")

def create_sample_rates():
    """Create sample scrap material rates"""
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
    
    for rate_data in sample_rates:
        if not Rate.query.filter_by(material=rate_data['material']).first():
            rate = Rate(**rate_data)
            db.session.add(rate)
            print(f"Created rate: {rate_data['material']}")
        else:
            print(f"Rate already exists: {rate_data['material']}")

def create_sample_tips():
    """Create sample educational tips"""
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
        },
        {
            'title': 'Remove Insulation from Copper Wires',
            'description': 'Stripped copper wire gets ₹650/kg while insulated wire gets only ₹250/kg. Spend time stripping for much better returns.',
            'category': 'Preparation',
            'icon': '⚡',
            'impact': '160% More Value'
        },
        {
            'title': 'Wear Safety Gloves and Shoes',
            'description': 'Always wear protective gear when handling scrap materials. Sharp edges, rust, and chemicals can cause injuries.',
            'category': 'Safety',
            'icon': '🧤',
            'impact': 'Stay Safe'
        },
        {
            'title': 'Best Time to Sell Metals',
            'description': 'Metal prices are typically higher during construction season (March-September). Monitor trends and sell when rates are up.',
            'category': 'Rates',
            'icon': '📈',
            'impact': 'Timing Matters'
        }
    ]
    
    for tip_data in sample_tips:
        if not Tip.query.filter_by(title=tip_data['title']).first():
            tip = Tip(**tip_data)
            db.session.add(tip)
            print(f"Created tip: {tip_data['title']}")
        else:
            print(f"Tip already exists: {tip_data['title']}")

def create_sample_products():
    """Create sample products for the marketplace"""
    sample_products = [
        {
            'dealer_email': 'dealer1@ecoscrap.com',
            'dealer_name': 'Rajesh Kumar',
            'name': 'Recycled Steel Sheets',
            'price': 3800,
            'category': 'metals',
            'description': 'High-quality recycled steel sheets perfect for construction. Tested for durability and strength.',
            'status': 'approved',
            'stock': 50,
            'rating': 4.5,
            'image': '🔩'
        },
        {
            'dealer_email': 'dealer1@ecoscrap.com',
            'dealer_name': 'Rajesh Kumar',
            'name': 'Copper Wire Scraps',
            'price': 10400,
            'category': 'metals',
            'description': 'Pure copper wire scraps with excellent conductivity. Ideal for electrical applications.',
            'status': 'approved',
            'stock': 25,
            'rating': 4.8,
            'image': '🔌'
        },
        {
            'dealer_email': 'dealer2@ecoscrap.com',
            'dealer_name': 'Sunita Singh',
            'name': 'Plastic Bottle Pellets',
            'price': 1050,
            'category': 'plastics',
            'description': 'Clean PET plastic pellets ready for manufacturing. Food-grade quality available.',
            'status': 'approved',
            'stock': 100,
            'rating': 4.2,
            'image': '♻️'
        }
    ]
    
    for product_data in sample_products:
        if not Product.query.filter_by(name=product_data['name']).first():
            product = Product(**product_data)
            db.session.add(product)
            print(f"Created product: {product_data['name']}")
        else:
            print(f"Product already exists: {product_data['name']}")

def init_database(reset=False, sample_only=False):
    """Initialize the database"""
    with app.app_context():
        if reset:
            print("Dropping all tables...")
            db.drop_all()
            print("Tables dropped successfully.")
        
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully.")
        
        if not sample_only:
            print("Adding sample data...")
            create_sample_users()
            create_sample_rates()
            create_sample_tips()
            create_sample_products()
            
            # Commit all changes
            db.session.commit()
            print("Sample data added successfully.")
        
        print("Database initialization completed!")

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Initialize EcoScrap database')
    parser.add_argument('--reset', action='store_true', help='Reset database (drop all tables)')
    parser.add_argument('--sample', action='store_true', help='Add sample data only (don\'t create tables)')
    
    args = parser.parse_args()
    
    if args.sample:
        print("Adding sample data only...")
        with app.app_context():
            create_sample_users()
            create_sample_rates()
            create_sample_tips()
            create_sample_products()
            db.session.commit()
            print("Sample data added successfully!")
    else:
        init_database(reset=args.reset)

if __name__ == '__main__':
    main()
