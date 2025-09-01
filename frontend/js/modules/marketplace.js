/**
 * EcoScrap Application - Marketplace Module
 * =========================================
 * 
 * This module handles all marketplace functionality including shopping cart management,
 * product browsing, order processing, and checkout operations. It provides a complete
 * e-commerce experience for customers to purchase recycled materials from dealers.
 * 
 * Key Features:
 * - Shopping Cart Management: Add, remove, and update cart items
 * - Product Browsing: Search, filter, and view product listings
 * - Order Processing: Checkout flow and order management
 * - Stock Management: Real-time stock validation
 * - Payment Integration: Multiple payment method support
 * 
 * User Interactions:
 * - Add products to cart with quantity validation
 * - Update cart item quantities
 * - Remove items from cart
 * - Proceed to checkout with order summary
 * - Complete payment and place orders
 * 
 * Business Logic:
 * - Stock validation prevents overselling
 * - Quantity limits based on available inventory
 * - Tax calculation (18% GST for Indian market)
 * - Order total computation with proper formatting
 * 
 * Data Flow:
 * 1. Product selection and cart addition
 * 2. Cart management and quantity updates
 * 3. Checkout process with order summary
 * 4. Payment method selection
 * 5. Order placement and confirmation
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// SHOPPING CART MANAGEMENT
// ========================================
/**
 * Add a product to the shopping cart
 * 
 * This function handles adding products to the user's shopping cart with
 * comprehensive validation including user authentication, product availability,
 * and stock level checks. It also handles duplicate items intelligently.
 * 
 * Add to Cart Process:
 * 1. Verify user authentication and customer role
 * 2. Validate product existence and availability
 * 3. Check stock levels for purchase
 * 4. Handle duplicate items by incrementing quantity
 * 5. Update cart state and persist changes
 * 6. Provide user feedback and UI updates
 * 
 * Validation Rules:
 * - User must be logged in with customer role
 * - Product must exist and be in stock
 * - Quantity cannot exceed available stock
 * - Duplicate items increment quantity safely
 * 
 * Security Features:
 * - Role-based access control (customers only)
 * - Stock validation prevents overselling
 * - User authentication required
 * 
 * @param {string|number} productId - Unique identifier of the product to add
 * @returns {void} - No return value, updates cart state directly
 */
function addToCart(productId) {
    // Verify user is logged in and has customer role
    // Only customers can purchase products in the marketplace
    if (!appState.isLoggedIn || appState.currentUser.role !== 'customer') {
        showModal('loginModal');
        return;
    }

    // Find product in database by ID
    // Product lookup ensures data integrity and availability
    const products = Database.getProducts();
    const product = products.find(p => p.id == productId);
    
    if (!product) {
        showNotification('Product not found', 'error');
        return;
    }

    // Check product stock availability before adding to cart
    // This prevents adding out-of-stock items and maintains inventory accuracy
    if (!product.stock || product.stock <= 0) {
        showNotification('Product is out of stock', 'error');
        return;
    }

    // Check if item already exists in cart to handle duplicates
    // Existing items increment quantity instead of creating duplicates
    const existingItem = appState.cart.find(item => item.id == productId);
    
    if (existingItem) {
        // Increment quantity if item exists, but respect stock limits
        // This prevents cart quantities from exceeding available inventory
        if (existingItem.quantity >= product.stock) {
            showNotification('Cannot add more items than available stock', 'error');
            return;
        }
        existingItem.quantity += 1;
    } else {
        // Add new item to cart with essential product information
        // Only necessary data is stored in cart for performance
        appState.cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            image: product.image,
            dealerName: product.dealerName,
            quantity: 1
        });
    }

    // Persist cart changes to localStorage and update UI
    // This ensures cart state survives page refreshes
    Database.saveCart(appState.cart);
    updateCartCount();
    showNotification(`${product.name} added to cart!`, 'success');
}

/**
 * Update the quantity of a cart item
 * 
 * This function handles quantity changes for items in the shopping cart,
 * including increment/decrement operations with proper stock validation.
 * It automatically removes items when quantity reaches zero.
 * 
 * Quantity Update Process:
 * 1. Locate cart item by product ID
 * 2. Calculate new quantity based on change parameter
 * 3. Validate against available stock
 * 4. Update quantity or remove item if zero
 * 5. Persist changes and update UI
 * 
 * Change Parameter:
 * - Positive values: Increase quantity
 * - Negative values: Decrease quantity
 * - Zero or negative result: Remove item from cart
 * 
 * Validation Features:
 * - Stock level validation prevents overselling
 * - Automatic item removal for zero quantities
 * - Real-time cart updates and persistence
 * 
 * @param {string|number} productId - ID of the product to update quantity
 * @param {number} change - Quantity change (positive for increase, negative for decrease)
 * @returns {void} - No return value, updates cart state directly
 */
function updateQuantity(productId, change) {
    // Find the cart item to update
    const item = appState.cart.find(item => item.id == productId);
    if (!item) return;

    // Calculate new quantity based on requested change
    const newQuantity = item.quantity + change;
    
    // Remove item if quantity becomes zero or negative
    // This keeps cart clean and prevents invalid quantities
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }

    // Validate against available stock to prevent overselling
    // Stock check ensures inventory accuracy and prevents fulfillment issues
    const product = Database.getProducts().find(p => p.id == productId);
    if (product && newQuantity > product.stock) {
        showNotification('Cannot exceed available stock', 'error');
        return;
    }

    // Update quantity and persist changes to localStorage
    // UI updates ensure immediate visual feedback
    item.quantity = newQuantity;
    Database.saveCart(appState.cart);
    updateCartCount();
    loadCart(); // Reload cart display to reflect changes
}

/**
 * Remove a product from the shopping cart
 * 
 * This function completely removes a specified item from the shopping cart,
 * updates the cart state, and refreshes the UI to reflect the changes.
 * 
 * Removal Process:
 * 1. Filter out the specified product from cart array
 * 2. Update cart state in application memory
 * 3. Persist changes to localStorage
 * 4. Update cart count display
 * 5. Reload cart display for immediate feedback
 * 6. Show removal confirmation to user
 * 
 * Data Management:
 * - Complete item removal (not just quantity zero)
 * - Cart state synchronization
 * - Persistent storage updates
 * - UI consistency maintenance
 * 
 * @param {string|number} productId - ID of the product to remove from cart
 * @returns {void} - No return value, updates cart state directly
 */
function removeFromCart(productId) {
    // Filter out the specified item from cart array
    // This creates a new array without the removed item
    appState.cart = appState.cart.filter(item => item.id != productId);
    
    // Persist cart changes and update UI components
    // This ensures changes survive page refreshes
    Database.saveCart(appState.cart);
    updateCartCount();
    loadCart(); // Reload cart display to show updated state
    showNotification('Item removed from cart', 'info');
}

// ========================================
// CHECKOUT PROCESSING
// ========================================
/**
 * Initiate the checkout process
 * 
 * This function starts the checkout flow by validating cart contents,
 * pre-filling user information, and displaying the checkout modal
 * with order summary and payment options.
 * 
 * Checkout Initiation Process:
 * 1. Validate cart has items before proceeding
 * 2. Pre-fill delivery address from user profile
 * 3. Update order summary with current cart contents
 * 4. Display checkout modal for user completion
 * 
 * User Experience Features:
 * - Address pre-filling reduces form completion time
 * - Order summary provides clear cost breakdown
 * - Modal presentation focuses user attention
 * - Validation prevents empty cart checkout
 * 
 * Pre-fill Logic:
 * - Uses current user's stored address
 * - Automatically populates address field
 * - Maintains user convenience
 * 
 * @returns {void} - No return value, displays checkout interface
 */
function proceedToCheckout() {
    // Ensure cart has items before proceeding to checkout
    // Empty cart checkout would result in invalid orders
    if (appState.cart.length === 0) {
        showNotification('Your cart is empty', 'error');
        return;
    }
    
    // Pre-fill delivery address from user profile for convenience
    // This reduces form completion time and improves user experience
    const addressField = document.querySelector('#checkoutForm textarea[name="address"]');
    if (addressField && appState.currentUser.address) {
        addressField.value = appState.currentUser.address;
    }
    
    // Update order summary and show checkout modal
    // Order summary provides clear cost breakdown before payment
    updateOrderSummary();
    showModal('checkoutModal');
}

/**
 * Update the order summary display in checkout modal
 * 
 * This function calculates and displays the complete order breakdown
 * including individual items, subtotal, tax calculations, and final total.
 * It provides transparent pricing information to customers.
 * 
 * Order Summary Components:
 * 1. Individual item details (name, quantity, price)
 * 2. Subtotal calculation (sum of all items)
 * 3. Tax calculation (18% GST for Indian market)
 * 4. Final total (subtotal + tax)
 * 
 * Calculation Logic:
 * - Subtotal: Sum of (price × quantity) for all items
 * - Tax: 18% GST applied to subtotal
 * - Total: Subtotal + tax amount
 * 
 * Display Features:
 * - Formatted currency values with proper symbols
 * - Clear item-by-item breakdown
 * - Tax transparency for compliance
 * - Professional order summary layout
 * 
 * @returns {void} - No return value, updates order summary display
 */
function updateOrderSummary() {
    const orderSummary = document.getElementById('orderSummary');
    if (!orderSummary) return;

    // Calculate order totals with proper mathematical operations
    // Subtotal is sum of all item costs (price × quantity)
    const subtotal = appState.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    // Apply 18% GST tax rate (Indian Goods and Services Tax)
    // Tax calculation ensures compliance with local regulations
    const tax = subtotal * 0.18;
    
    // Final total includes subtotal and tax
    const total = subtotal + tax;

    // Generate HTML for order summary display
    // Each section provides clear information for customer review
    orderSummary.innerHTML = `
        <h4>Order Summary</h4>
        ${appState.cart.map(item => `
            <div class="summary-item">
                <span>${item.name} × ${item.quantity}</span>
                <span>₹${(item.price * item.quantity).toLocaleString()}</span>
            </div>
        `).join('')}
        <div class="summary-item">
            <span>Subtotal</span>
            <span>₹${subtotal.toLocaleString()}</span>
        </div>
        <div class="summary-item">
            <span>GST (18%)</span>
            <span>₹${tax.toFixed(2)}</span>
        </div>
        <div class="summary-item summary-total">
            <span>Total</span>
            <span>₹${total.toFixed(2)}</span>
        </div>
    `;
}

// ========================================
// MARKETPLACE DISPLAY FUNCTIONS
// ========================================
/**
 * Load and display marketplace products
 * 
 * This function populates the marketplace grid with available products,
 * applying any active filters and search criteria. It creates the
 * product display interface for customer browsing.
 * 
 * Marketplace Loading Process:
 * 1. Retrieve products from database
 * 2. Apply category and search filters
 * 3. Generate product cards with details
 * 4. Display products in responsive grid layout
 * 5. Handle empty product states
 * 
 * Product Display Features:
 * - Product images and names
 * - Pricing information
 * - Stock availability
 * - Dealer information
 * - Add to cart functionality
 * 
 * Filtering Capabilities:
 * - Category-based filtering
 * - Search term matching
 * - Status-based filtering (approved products only)
 * 
 * @returns {void} - No return value, updates marketplace display
 */
function loadMarketplace() {
    const productsGrid = document.getElementById('productsGrid');
    if (!productsGrid) return;

    const products = Database.getProducts().filter(p => p.status === 'approved');
    
    if (products.length === 0) {
        productsGrid.innerHTML = '<div class="empty-state">No products available at the moment.</div>';
        return;
    }

    productsGrid.innerHTML = products.map(product => `
        <div class="product-card" data-category="${product.category}" data-name="${product.name.toLowerCase()}">
            <div class="product-image">${product.image || '📦'}</div>
            <div class="product-info">
                <h3 class="product-title">${product.name}</h3>
                <p class="product-price">₹${product.price}</p>
                <p style="color: var(--eco-text-light); margin-bottom: 8px;">By: ${product.dealerName || 'Verified Dealer'}</p>
                <p style="margin-bottom: 16px;">${product.description}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <span style="color: var(--eco-text-light); font-size: 14px;">Stock: ${product.stock || 'Available'}</span>
                    <span style="color: var(--eco-secondary);">★ ${product.rating || '4.0'}</span>
                </div>
                <div class="product-actions">
                    <button class="btn btn--primary btn--sm" onclick="addToCart(${product.id})" 
                            ${!product.stock ? 'disabled' : ''}>
                        ${!product.stock ? 'Out of Stock' : 'Add to Cart'}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterProducts() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('categoryFilter')?.value || '';
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const name = card.getAttribute('data-name') || '';
        const category = card.getAttribute('data-category') || '';
        
        const matchesSearch = name.includes(searchTerm);
        const matchesCategory = !categoryFilter || category === categoryFilter;
        
        if (matchesSearch && matchesCategory) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Cart Display Functions
function loadCart() {
    const cartContent = document.getElementById('cartContent');
    if (!cartContent) return;

    if (appState.cart.length === 0) {
        cartContent.innerHTML = `
            <div class="cart-empty">
                <div style="font-size: 64px; margin-bottom: 16px;">🛒</div>
                <h3>Your cart is empty</h3>
                <p>Browse our marketplace to add some items!</p>
                <button class="btn btn--primary" onclick="showSection('marketplace')">Go to Marketplace</button>
            </div>`;
        return;
    }

    const total = appState.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax = total * 0.18; // 18% GST
    const finalTotal = total + tax;

    cartContent.innerHTML = `
        <div class="cart-items">
            ${appState.cart.map(item => `
                <div class="cart-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <div style="font-size: 40px;">${item.image || '📦'}</div>
                            <div>
                                <h4>${item.name}</h4>
                                <p style="color: var(--color-text-secondary); margin: 0; font-size: 14px;">
                                    By: ${item.dealerName || 'Verified Dealer'}
                                </p>
                                <p style="color: var(--color-text-secondary); margin: 0;">₹${item.price} × ${item.quantity}</p>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <button class="btn btn--outline btn--sm" onclick="updateQuantity(${item.id}, -1)">−</button>
                            <span style="min-width: 30px; text-align: center;">${item.quantity}</span>
                            <button class="btn btn--outline btn--sm" onclick="updateQuantity(${item.id}, 1)">+</button>
                            <button class="btn btn--outline btn--sm" onclick="removeFromCart(${item.id})" 
                                    style="color: var(--color-error); margin-left: 8px;">Remove</button>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="cart-summary">
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>Subtotal:</span>
                    <span>₹${total.toFixed(2)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>GST (18%):</span>
                    <span>₹${tax.toFixed(2)}</span>
                </div>
                <hr>
                <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 18px;">
                    <span>Total:</span>
                    <span>₹${finalTotal.toFixed(2)}</span>
                </div>
            </div>
            <button class="btn btn--primary btn--full-width" onclick="proceedToCheckout()">Proceed to Checkout</button>
        </div>
    `;
}

// Product Management Functions
function handleAddProduct(e) {
    e.preventDefault();
    
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    
    const product = {
        name: formData.get('name'),
        category: formData.get('category'),
        price: parseFloat(formData.get('price')),
        stock: parseInt(formData.get('stock')),
        description: formData.get('description'),
        dealerEmail: appState.currentUser.email,
        dealerName: appState.currentUser.name,
        status: 'pending',
        image: getCategoryIcon(formData.get('category'))
    };
    
    Database.saveProduct(product);
    showNotification('Product added successfully! Awaiting admin approval.', 'success');
    e.target.reset();
}

function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        Database.deleteProduct(productId);
        loadDealerProducts();
        showNotification('Product deleted successfully', 'success');
    }
}

function approveProduct(productId) {
    const products = Database.getProducts();
    const product = products.find(p => p.id == productId);
    if (product) {
        product.status = 'approved';
        Database.saveProduct(product);
        loadProductManagement();
        showNotification('Product approved successfully', 'success');
    }
}

function rejectProduct(productId) {
    const products = Database.getProducts();
    const product = products.find(p => p.id == productId);
    if (product) {
        product.status = 'rejected';
        Database.saveProduct(product);
        loadProductManagement();
        showNotification('Product rejected', 'info');
    }
}

function getCategoryIcon(category) {
    const icons = {
        'metals': '🔩',
        'plastics': '♻️',
        'paper': '📦',
        'electronics': '💾'
    };
    return icons[category] || '📦';
}
