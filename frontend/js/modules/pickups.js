/**
 * EcoScrap Application - Pickups Module
 * 
 * This module handles all pickup-related functionality including scheduling,
 * order processing, payment validation, and pickup management. It provides
 * a complete system for customers to book scrap pickups and for dealers
 * to manage pickup requests.
 * 
 * Key Features:
 * - Pickup Scheduling: Book scrap collection appointments
 * - Order Processing: Complete checkout and payment flow
 * - Payment Validation: Validate different payment methods
 * - Value Estimation: Calculate estimated scrap value
 * - Pickup Management: Track and manage pickup requests
 * 
 * User Workflows:
 * - Customer: Book pickups, estimate values, complete orders
 * - Dealer: View pickup requests, manage collections
 * - Admin: Monitor pickup operations and transactions
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// PICKUP SCHEDULING
// ========================================
/**
 * Handle pickup booking form submission
 * Validates user authentication and form data
 * Creates pickup record with estimated value calculation
 * 
 * @param {Event} e - Form submission event
 */
function handlePickupBooking(e) {
    e.preventDefault();
    
    // Ensure user is logged in before booking pickup
    if (!appState.isLoggedIn) {
        showModal('loginModal');
        return;
    }
    
    // Validate form data before processing
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    
    // Create pickup object with calculated estimated value
    const pickup = {
        material: formData.get('material'),
        weight: parseInt(formData.get('weight')),
        date: formData.get('date'),
        time: formData.get('time'),
        address: formData.get('address'),
        estimatedValue: calculateEstimatedValue(formData.get('material'), formData.get('weight'))
    };
    
    // Save pickup to database and provide feedback
    Database.savePickup(pickup);
    showNotification('Pickup booked successfully!', 'success');
    e.target.reset();
    document.getElementById('estimatedValue').classList.add('hidden');
}

/**
 * Calculate and display real-time estimate for pickup value
 * Updates estimate display as user selects material and weight
 * Provides immediate feedback on potential scrap value
 */
function calculateEstimate() {
    const materialSelect = document.querySelector('#quickPickupForm select[name="material"]');
    const weightInput = document.querySelector('#quickPickupForm input[name="weight"]');
    const estimatedValue = document.getElementById('estimatedValue');
    const estimatedAmount = document.getElementById('estimatedAmount');
    
    // Only calculate if both material and weight are provided
    if (materialSelect && weightInput && materialSelect.value && weightInput.value) {
        const material = materialSelect.value;
        const weight = parseFloat(weightInput.value);
        const rates = Database.getRates();
        const rate = rates.find(r => r.material.toLowerCase() === material);
        
        // Calculate and display estimate if valid data
        if (rate && weight > 0) {
            const estimate = rate.ratePerKg * weight;
            estimatedAmount.textContent = estimate.toFixed(2);
            estimatedValue.classList.remove('hidden');
        }
    } else {
        // Hide estimate if incomplete data
        estimatedValue.classList.add('hidden');
    }
}

/**
 * Calculate estimated value for scrap materials
 * Uses current market rates to determine potential value
 * 
 * @param {string} material - Type of scrap material
 * @param {number} weight - Weight in kilograms
 * @returns {number} Estimated value in Indian Rupees
 */
function calculateEstimatedValue(material, weight) {
    const rates = Database.getRates();
    const rate = rates.find(r => r.material.toLowerCase() === material);
    return rate ? rate.ratePerKg * weight : 0;
}

// ========================================
// ORDER PROCESSING
// ========================================
/**
 * Handle checkout form submission and order completion
 * Validates payment method and processes transaction
 * Creates order record and clears shopping cart
 * 
 * @param {Event} e - Form submission event
 */
function handleCheckout(e) {
    e.preventDefault();
    
    // Validate form data before processing
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    const paymentMethod = formData.get('payment');
    
    // Validate payment method specific fields
    if (!validatePaymentMethod(paymentMethod, formData)) {
        return;
    }
    
    // Calculate order totals
    const subtotal = appState.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax = subtotal * 0.18; // 18% GST tax rate
    const total = subtotal + tax;
    
    // Create transaction record
    const transaction = {
        customerEmail: appState.currentUser.email,
        customerName: appState.currentUser.name,
        items: [...appState.cart],
        amount: total,
        paymentMethod: getPaymentMethodDisplay(paymentMethod),
        address: formData.get('address'),
        status: paymentMethod === 'cod' ? 'pending' : 'completed' // COD orders are pending until delivery
    };
    
    // Save transaction and clear cart
    const savedTransaction = Database.saveTransaction(transaction);
    
    // Clear cart and update UI
    appState.cart = [];
    Database.saveCart(appState.cart);
    updateCartCount();
    
    // Show success confirmation
    document.getElementById('orderIdText').textContent = `Order ID: ${savedTransaction.id}`;
    closeModal();
    showModal('paymentSuccessModal');
    
    showNotification('Order placed successfully!', 'success');
}

// Payment Functions
function handlePaymentMethodChange() {
    const paymentMethod = document.getElementById('paymentMethod').value;
    const allDetails = document.querySelectorAll('.payment-details');
    
    allDetails.forEach(detail => detail.classList.add('hidden'));
    
    if (paymentMethod === 'upi') {
        document.getElementById('upiDetails')?.classList.remove('hidden');
    } else if (paymentMethod === 'card') {
        document.getElementById('cardDetails')?.classList.remove('hidden');
    } else if (paymentMethod === 'netbanking') {
        document.getElementById('netbankingDetails')?.classList.remove('hidden');
    }
}

function validatePaymentMethod(paymentMethod, formData) {
    if (paymentMethod === 'upi') {
        const upiId = formData.get('upiId');
        if (!upiId || !upiId.includes('@')) {
            showNotification('Please enter a valid UPI ID', 'error');
            return false;
        }
    } else if (paymentMethod === 'card') {
        const cardNumber = formData.get('cardNumber');
        const cardExpiry = formData.get('cardExpiry');
        const cardCvv = formData.get('cardCvv');
        const cardName = formData.get('cardName');
        
        if (!cardNumber || cardNumber.replace(/\s/g, '').length < 16) {
            showNotification('Please enter a valid card number', 'error');
            return false;
        }
        if (!cardExpiry || !/^\d{2}\/\d{2}$/.test(cardExpiry)) {
            showNotification('Please enter a valid expiry date (MM/YY)', 'error');
            return false;
        }
        if (!cardCvv || cardCvv.length < 3) {
            showNotification('Please enter a valid CVV', 'error');
            return false;
        }
        if (!cardName) {
            showNotification('Please enter the cardholder name', 'error');
            return false;
        }
    } else if (paymentMethod === 'netbanking') {
        const bank = formData.get('bank');
        if (!bank) {
            showNotification('Please select a bank', 'error');
            return false;
        }
    }
    return true;
}

function getPaymentMethodDisplay(method) {
    const methods = {
        'cod': 'Cash on Delivery',
        'upi': 'UPI Payment',
        'card': 'Credit/Debit Card',
        'netbanking': 'Net Banking'
    };
    return methods[method] || method;
}

function setupCardFormatting() {
    const cardNumberInput = document.querySelector('input[name="cardNumber"]');
    const cardExpiryInput = document.querySelector('input[name="cardExpiry"]');
    
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });
    }
    
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }
}

// Data Loading Functions
function loadCustomerOrders() {
    const ordersList = document.getElementById('ordersList');
    if (!ordersList) return;

    const orders = Database.getTransactions()
        .filter(t => t.customerEmail === appState.currentUser.email)
        .sort((a, b) => new Date(b.timestamp || b.date) - new Date(a.timestamp || a.date));

    if (orders.length === 0) {
        ordersList.innerHTML = '<div class="empty-state">No orders found. Start shopping in the marketplace!</div>';
        return;
    }

    ordersList.innerHTML = orders.map(order => `
        <div class="order-item">
            <div class="item-details">
                <h4>Order #${order.id}</h4>
                <p>Date: ${new Date(order.timestamp || order.date).toLocaleDateString()}</p>
                <p>Payment: ${order.paymentMethod || 'N/A'}</p>
            </div>
            <div class="item-amount">
                <span class="status status--${order.status === 'completed' ? 'success' : 'info'}">
                    ${order.status || 'Processing'}
                </span>
                <strong>₹${order.amount?.toLocaleString()}</strong>
            </div>
        </div>
    `).join('');
}

function loadCustomerPickups() {
    const pickupsList = document.getElementById('pickupsList');
    if (!pickupsList) return;

    const pickups = Database.getPickups()
        .filter(p => p.userEmail === appState.currentUser.email)
        .sort((a, b) => new Date(b.bookedDate) - new Date(a.bookedDate));

    if (pickups.length === 0) {
        pickupsList.innerHTML = '<div class="empty-state">No pickup requests found. Book your first pickup!</div>';
        return;
    }

    pickupsList.innerHTML = pickups.map(pickup => `
        <div class="pickup-item">
            <div class="item-details">
                <h4>${pickup.material} - ${pickup.weight}kg</h4>
                <p>Pickup Date: ${pickup.date} (${pickup.time})</p>
                <p>Address: ${pickup.address}</p>
            </div>
            <div class="item-amount">
                <span class="status status--${pickup.status === 'completed' ? 'success' : 
                    pickup.status === 'scheduled' ? 'info' : 'warning'}">
                    ${pickup.status}
                </span>
                <strong>₹${pickup.estimatedValue || 0}</strong>
            </div>
        </div>
    `).join('');
}

function loadDealerOrders() {
    const dealerOrdersList = document.getElementById('dealerOrdersList');
    if (!dealerOrdersList) return;

    const orders = Database.getTransactions()
        .filter(t => t.dealerEmail === appState.currentUser.email)
        .sort((a, b) => new Date(b.timestamp || b.date) - new Date(a.timestamp || a.date));

    if (orders.length === 0) {
        dealerOrdersList.innerHTML = '<div class="empty-state">No orders received yet.</div>';
        return;
    }

    dealerOrdersList.innerHTML = orders.map(order => `
        <div class="order-item">
            <div class="item-details">
                <h4>Order #${order.id}</h4>
                <p>Customer: ${order.customerName}</p>
                <p>Date: ${new Date(order.timestamp || order.date).toLocaleDateString()}</p>
            </div>
            <div class="item-amount">
                <span class="status status--${order.status === 'completed' ? 'success' : 'info'}">
                    ${order.status || 'Processing'}
                </span>
                <strong>₹${order.amount?.toLocaleString()}</strong>
            </div>
        </div>
    `).join('');
}

function loadDealerPickups() {
    const dealerPickupsList = document.getElementById('dealerPickupsList');
    if (!dealerPickupsList) return;

    const pickups = Database.getPickups()
        .sort((a, b) => new Date(b.bookedDate) - new Date(a.bookedDate));

    if (pickups.length === 0) {
        dealerPickupsList.innerHTML = '<div class="empty-state">No pickup requests available.</div>';
        return;
    }

    dealerPickupsList.innerHTML = pickups.map(pickup => `
        <div class="pickup-item">
            <div class="item-details">
                <h4>${pickup.material} - ${pickup.weight}kg</h4>
                <p>Customer: ${pickup.userName}</p>
                <p>Pickup Date: ${pickup.date} (${pickup.time})</p>
                <p>Address: ${pickup.address}</p>
            </div>
            <div class="item-amount">
                <span class="status status--${pickup.status === 'completed' ? 'success' : 
                    pickup.status === 'scheduled' ? 'info' : 'warning'}">
                    ${pickup.status}
                </span>
                <strong>₹${pickup.estimatedValue || 0}</strong>
            </div>
        </div>
    `).join('');
}
