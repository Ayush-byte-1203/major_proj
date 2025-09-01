"""
EcoScrap Application - Routes Package
=====================================

This package contains all the route modules for the EcoScrap application.
Each module handles a specific area of functionality and is organized
for better maintainability and code organization.

Modules:
- auth: Authentication and user management routes
- products: Product and marketplace routes
- pickups: Pickup scheduling routes
- transactions: Order and transaction routes
- admin: Administrative functions routes
- dashboard: Dashboard and analytics routes
- content: Content management routes

Package Structure:
routes/
├── __init__.py          # This file - package initialization
├── auth.py             # Authentication routes
├── products.py         # Product management routes
├── pickups.py          # Pickup scheduling routes
├── transactions.py     # Order processing routes
├── admin.py            # Administrative functions
├── dashboard.py        # Dashboard and analytics
└── content.py          # Content management

Usage:
    from routes.auth import auth_bp
    from routes.products import products_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

# Package initialization
# This file makes the routes directory a Python package
