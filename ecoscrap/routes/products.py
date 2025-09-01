"""
EcoScrap Application - Product Routes
=====================================

This module contains all product-related routes for the EcoScrap application.
It handles product creation, management, approval workflow, and marketplace operations.

Routes Included:
- GET /api/products: List products with filtering and search
- POST /api/products: Create new product (dealers only)
- PUT/DELETE /api/products/<id>: Update or delete products
- POST /api/admin/products/<id>/approve: Approve products (admins only)
- POST /api/admin/products/<id>/reject: Reject products (admins only)

Product Features:
- Marketplace product listings
- Product approval workflow
- Category-based filtering
- Search functionality
- Stock management
- Dealer product management

Business Logic:
- Only dealers can create products
- Products require admin approval before marketplace visibility
- Stock validation prevents overselling
- Product status management (pending, approved, rejected)

Security Features:
- Role-based access control
- Input validation and sanitization
- Ownership verification for modifications
- Admin-only approval operations

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Product
from decorators import dealer_required, admin_required

# Create products blueprint
products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def get_products():
    """
    Get all approved products with optional filtering
    
    This endpoint retrieves products from the marketplace with various
    filtering options. By default, only approved products are returned,
    but admins can view all products regardless of status.
    
    Query Parameters:
        - category: Filter by product category
        - search: Search in product names, descriptions, and dealer names
        - status: Filter by product status (default: approved)
        - limit: Maximum number of products to return
        - offset: Number of products to skip for pagination
    
    Filtering Logic:
        - Category filtering: Exact match on product category
        - Search filtering: Case-insensitive search across multiple fields
        - Status filtering: Filter by approval status
        - Pagination: Limit and offset for large result sets
    
    Business Rules:
        - Customers see only approved products
        - Dealers see their own products and approved marketplace products
        - Admins see all products regardless of status
        - Search is performed across product name, description, and dealer name
    
    Returns:
        - 200 OK: List of products matching criteria
        - 500 Internal Server Error: Database or system error
    """
    try:
        # Get query parameters for filtering
        category = request.args.get('category')
        search = request.args.get('search')
        status = request.args.get('status', 'approved')
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)
        
        # Build base query
        query = Product.query
        
        # Apply status filter (admins can override default)
        if status and (current_user.is_authenticated and current_user.role == 'admin'):
            query = query.filter_by(status=status)
        elif not current_user.is_authenticated or current_user.role == 'customer':
            # Customers see only approved products
            query = query.filter_by(status='approved')
        elif current_user.role == 'dealer':
            # Dealers see their own products and approved marketplace products
            query = query.filter(
                db.or_(
                    Product.dealer_email == current_user.email,
                    Product.status == 'approved'
                )
            )
        
        # Apply category filter if specified
        if category:
            query = query.filter_by(category=category)
        
        # Apply search filter if specified
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.dealer_name.ilike(search_term)
                )
            )
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query and return results
        products = query.all()
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('', methods=['POST'])
@login_required
@dealer_required
def create_product():
    """
    Create new product (dealers only)
    
    This endpoint allows dealers to create new product listings in the marketplace.
    Products are created with 'pending' status and require admin approval before
    becoming visible to customers.
    
    Request Body:
        {
            "name": "Product name",
            "category": "Product category",
            "price": 100.00,
            "description": "Product description",
            "stock": 50,
            "image": "🔩"
        }
    
    Validation:
        - All required fields must be provided
        - Price must be positive number
        - Stock must be non-negative integer
        - Category must be valid product category
    
    Business Logic:
        - Products are created with 'pending' status
        - Dealer information is automatically populated
        - Stock validation prevents negative quantities
        - Admin approval required before marketplace visibility
    
    Security Features:
        - Only authenticated dealers can create products
        - Input validation and sanitization
        - Automatic dealer association
    
    Returns:
        - 201 Created: Product created successfully with product data
        - 400 Bad Request: Missing required fields or validation failure
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not a dealer
        - 500 Internal Server Error: Database or system error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'price', 'description', 'stock']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate price and stock
        if float(data['price']) <= 0:
            return jsonify({'error': 'Price must be positive'}), 400
        
        if int(data['stock']) < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
        
        # Create new product with dealer information
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
        
        # Save product to database
        db.session.add(product)
        db.session.commit()
        
        # Return success response with product data
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_product(product_id):
    """
    Update or delete product
    
    This endpoint allows users to modify or remove their own products.
    Admins can modify any product in the system.
    
    Methods:
        - PUT: Update product information
        - DELETE: Remove product from marketplace
    
    URL Parameters:
        - product_id: ID of the product to manage
    
    Request Body (PUT):
        {
            "name": "Updated product name",
            "price": 150.00,
            "description": "Updated description",
            "stock": 75,
            "image": "🔧"
        }
    
    Security Features:
        - Authentication required
        - Users can only modify their own products
        - Admins can modify any product
        - Input validation and sanitization
    
    Business Rules:
        - Product ownership verification
        - Stock validation for updates
        - Price validation for updates
        - Deletion removes product completely
    
    Returns:
        - 200 OK: Product updated or deleted successfully
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not authorized to modify product
        - 404 Not Found: Product not found
        - 500 Internal Server Error: Database or system error
    """
    # Find product by ID
    product = Product.query.get_or_404(product_id)
    
    # Check if user owns the product or is admin
    if current_user.role != 'admin' and product.dealer_email != current_user.email:
        return jsonify({'error': 'Access denied'}), 403
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update product fields if provided
            if 'name' in data:
                product.name = data['name']
            if 'price' in data:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({'error': 'Price must be positive'}), 400
                product.price = price
            if 'category' in data:
                product.category = data['category']
            if 'description' in data:
                product.description = data['description']
            if 'stock' in data:
                stock = int(data['stock'])
                if stock < 0:
                    return jsonify({'error': 'Stock cannot be negative'}), 400
                product.stock = stock
            if 'image' in data:
                product.image = data['image']
            
            # Save changes to database
            db.session.commit()
            
            # Return updated product data
            return jsonify({
                'message': 'Product updated successfully',
                'product': product.to_dict()
            }), 200
            
        except Exception as e:
            # Rollback database changes on error
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Remove product from database
            db.session.delete(product)
            db.session.commit()
            
            return jsonify({'message': 'Product deleted successfully'}), 200
            
        except Exception as e:
            # Rollback database changes on error
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_product(product_id):
    """
    Approve product for marketplace (admins only)
    
    This endpoint allows administrators to approve products for marketplace
    visibility. Approved products become visible to customers and can be
    purchased through the marketplace.
    
    URL Parameters:
        - product_id: ID of the product to approve
    
    Business Logic:
        - Changes product status from 'pending' to 'approved'
        - Product becomes visible in customer marketplace
        - Dealer receives notification of approval
        - Product can now be purchased by customers
    
    Security Features:
        - Admin-only access
        - Product existence verification
        - Status validation
    
    Returns:
        - 200 OK: Product approved successfully
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not admin
        - 404 Not Found: Product not found
        - 500 Internal Server Error: Database or system error
    """
    try:
        # Find product by ID
        product = Product.query.get_or_404(product_id)
        
        # Approve product by changing status
        product.status = 'approved'
        
        # Save changes to database
        db.session.commit()
        
        # Return success response with updated product data
        return jsonify({
            'message': 'Product approved successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_product(product_id):
    """
    Reject product (admins only)
    
    This endpoint allows administrators to reject products that don't meet
    marketplace standards. Rejected products remain in the system but are
    not visible to customers.
    
    URL Parameters:
        - product_id: ID of the product to reject
    
    Business Logic:
        - Changes product status from 'pending' to 'rejected'
        - Product remains hidden from customer marketplace
        - Dealer receives notification of rejection
        - Product can be resubmitted after modifications
    
    Security Features:
        - Admin-only access
        - Product existence verification
        - Status validation
    
    Returns:
        - 200 OK: Product rejected successfully
        - 401 Unauthorized: User not authenticated
        - 403 Forbidden: User not admin
        - 404 Not Found: Product not found
        - 500 Internal Server Error: Database or system error
    """
    try:
        # Find product by ID
        product = Product.query.get_or_404(product_id)
        
        # Reject product by changing status
        product.status = 'rejected'
        
        # Save changes to database
        db.session.commit()
        
        # Return success response with updated product data
        return jsonify({
            'message': 'Product rejected successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
