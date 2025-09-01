/**
 * EcoScrap Application - Dashboard Module
 * 
 * This module provides comprehensive dashboard functionality for different user roles
 * including dealers and administrators. It handles analytics, reporting, user management,
 * and product administration with role-based access control.
 * 
 * Key Features:
 * - Dealer Dashboard: Business metrics and product management
 * - Admin Dashboard: Platform overview and system administration
 * - User Management: Admin user administration and status control
 * - Product Management: Product approval and moderation system
 * - Analytics: Revenue tracking and performance metrics
 * 
 * Dashboard Types:
 * - Dealer Dashboard: Business performance and product analytics
 * - Admin Dashboard: Platform-wide statistics and management
 * - User Management: User administration and control
 * - Product Management: Product moderation and approval
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// DEALER DASHBOARD
// ========================================
/**
 * Load and display dealer dashboard with business metrics
 * Shows product counts, earnings, pending approvals, and order statistics
 * Provides dealers with comprehensive business overview
 */
function loadDealerDashboard() {
    const dealerStats = document.getElementById('dealerStats');
    if (!dealerStats) return;

    // Get dealer-specific data from database
    const products = Database.getProducts().filter(p => p.dealerEmail === appState.currentUser.email);
    const transactions = Database.getTransactions().filter(t => t.dealerEmail === appState.currentUser.email);
    const earnings = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
    const pendingProducts = products.filter(p => p.status === 'pending').length;

    // Display business metrics in stat cards
    dealerStats.innerHTML = `
        <div class="stat-card">
            <h3>Total Products</h3>
            <p class="stat-value">${products.length}</p>
        </div>
        <div class="stat-card">
            <h3>Total Earnings</h3>
            <p class="stat-value">₹${earnings.toLocaleString()}</p>
        </div>
        <div class="stat-card">
            <h3>Pending Approval</h3>
            <p class="stat-value">${pendingProducts}</p>
        </div>
        <div class="stat-card">
            <h3>Orders Received</h3>
            <p class="stat-value">${transactions.length}</p>
        </div>
    `;
}

// ========================================
// ADMIN DASHBOARD
// ========================================
/**
 * Load and display admin dashboard with platform-wide statistics
 * Shows user counts, product totals, revenue, and pickup requests
 * Provides administrators with comprehensive platform overview
 */
function loadAdminDashboard() {
    const adminStats = document.getElementById('adminStats');
    if (!adminStats) return;

    // Get platform-wide data from database
    const users = Database.getUsers();
    const products = Database.getProducts();
    const transactions = Database.getTransactions();
    const pickups = Database.getPickups();
    const revenue = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);

    // Display platform metrics in stat cards
    adminStats.innerHTML = `
        <div class="stat-card">
            <h3>Total Users</h3>
            <p class="stat-value">${users.length}</p>
        </div>
        <div class="stat-card">
            <h3>Total Products</h3>
            <p class="stat-value">${products.length}</p>
        </div>
        <div class="stat-card">
            <h3>Total Revenue</h3>
            <p class="stat-value">₹${revenue.toLocaleString()}</p>
        </div>
        <div class="stat-card">
            <h3>Pickup Requests</h3>
            <p class="stat-value">${pickups.length}</p>
        </div>
    `;
}

// ========================================
// USER MANAGEMENT
// ========================================
/**
 * Load and display user management interface for administrators
 * Shows user table with actions for status control and management
 * Provides comprehensive user administration capabilities
 */
function loadUserManagement() {
    const usersTable = document.getElementById('usersTable');
    if (!usersTable) return;

    const users = Database.getUsers();
    
    // Create user management table with action buttons
    usersTable.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Join Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr>
                        <td>${user.name}</td>
                        <td>${user.email}</td>
                        <td><span class="status status--info">${user.role}</span></td>
                        <td><span class="status status--${user.status === 'active' ? 'success' : 'error'}">${user.status}</span></td>
                        <td>${user.joinDate || 'N/A'}</td>
                        <td>
                            <div class="item-actions">
                                <button class="btn btn--outline btn--sm" onclick="toggleUserStatus('${user.email}')">
                                    ${user.status === 'active' ? 'Block' : 'Activate'}
                                </button>
                                <button class="btn btn--outline btn--sm" onclick="editUser('${user.email}')">Edit</button>
                                ${user.email !== appState.currentUser.email ? 
                                    `<button class="btn btn--outline btn--sm" onclick="deleteUser('${user.email}')" 
                                             style="color: var(--color-error);">Delete</button>` : ''}
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function loadProductManagement() {
    const adminProductsList = document.getElementById('adminProductsList');
    if (!adminProductsList) return;

    const products = Database.getProducts()
        .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));

    if (products.length === 0) {
        adminProductsList.innerHTML = '<div class="empty-state">No products to review.</div>';
        return;
    }

    adminProductsList.innerHTML = products.map(product => `
        <div class="product-item">
            <div class="item-details">
                <h4>${product.name}</h4>
                <p>Dealer: ${product.dealerName} | Category: ${product.category}</p>
                <p>Price: ₹${product.price} | Stock: ${product.stock}</p>
                <p>${product.description}</p>
            </div>
            <div class="item-actions">
                <span class="status status--${product.status === 'approved' ? 'success' : 
                    product.status === 'pending' ? 'warning' : 'error'}">${product.status}</span>
                ${product.status === 'pending' ? `
                    <button class="btn btn--primary btn--sm" onclick="approveProduct(${product.id})">Approve</button>
                    <button class="btn btn--outline btn--sm" onclick="rejectProduct(${product.id})" 
                            style="color: var(--color-error);">Reject</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function loadAllTransactions() {
    const transactionsList = document.getElementById('transactionsList');
    if (!transactionsList) return;

    const transactions = Database.getTransactions()
        .sort((a, b) => new Date(b.timestamp || b.date) - new Date(a.timestamp || a.date));

    if (transactions.length === 0) {
        transactionsList.innerHTML = '<div class="empty-state">No transactions found.</div>';
        return;
    }

    transactionsList.innerHTML = transactions.map(transaction => `
        <div class="transaction-item">
            <div class="item-details">
                <h4>Transaction #${transaction.id}</h4>
                <p>Customer: ${transaction.customerName}</p>
                <p>Date: ${new Date(transaction.timestamp || transaction.date).toLocaleDateString()}</p>
                <p>Payment: ${transaction.paymentMethod}</p>
            </div>
            <div class="item-amount">
                <span class="status status--${transaction.status === 'completed' ? 'success' : 'info'}">
                    ${transaction.status || 'Processing'}
                </span>
                <strong>₹${transaction.amount?.toLocaleString()}</strong>
            </div>
        </div>
    `).join('');
}

function loadRatesManagement() {
    const ratesManagement = document.getElementById('ratesManagement');
    if (!ratesManagement) return;

    const rates = Database.getRates();
    
    ratesManagement.innerHTML = rates.map((rate, index) => `
        <div class="rate-management-item">
            <div class="rate-info">
                <span style="font-size: 24px; margin-right: 12px;">${rate.icon}</span>
                <div>
                    <h4>${rate.material}</h4>
                    <p style="color: var(--eco-text-light); margin: 0;">Current: ₹${rate.ratePerKg}/kg</p>
                </div>
            </div>
            <div class="rate-controls">
                <input type="number" class="form-control rate-input" value="${rate.ratePerKg}" 
                       id="rate-${index}" min="1" step="0.01">
                <select class="form-control" id="trend-${index}">
                    <option value="up" ${rate.trend === 'up' ? 'selected' : ''}>↗ Up</option>
                    <option value="stable" ${rate.trend === 'stable' ? 'selected' : ''}>→ Stable</option>
                    <option value="down" ${rate.trend === 'down' ? 'selected' : ''}>↘ Down</option>
                </select>
                <button class="btn btn--primary btn--sm" onclick="updateRate(${index})">Update</button>
            </div>
        </div>
    `).join('');
}

function updateRate(index) {
    const rates = Database.getRates();
    const newRate = parseFloat(document.getElementById(`rate-${index}`).value);
    const newTrend = document.getElementById(`trend-${index}`).value;
    
    if (newRate > 0) {
        rates[index].ratePerKg = newRate;
        rates[index].trend = newTrend;
        Database.saveRates(rates);
        showNotification('Rate updated successfully', 'success');
    }
}

// Dealer Product Management
function loadDealerProducts() {
    const dealerProductsList = document.getElementById('dealerProductsList');
    if (!dealerProductsList) return;

    const products = Database.getProducts()
        .filter(p => p.dealerEmail === appState.currentUser.email)
        .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));

    if (products.length === 0) {
        dealerProductsList.innerHTML = '<div class="empty-state">No products listed yet. Add your first product!</div>';
        return;
    }

    dealerProductsList.innerHTML = products.map(product => `
        <div class="product-item">
            <div class="item-details">
                <h4>${product.name}</h4>
                <p>Category: ${product.category} | Price: ₹${product.price} | Stock: ${product.stock}</p>
                <p>${product.description}</p>
            </div>
            <div class="item-actions">
                <span class="status status--${product.status === 'approved' ? 'success' : 
                    product.status === 'pending' ? 'warning' : 'error'}">${product.status}</span>
                <button class="btn btn--outline btn--sm" onclick="deleteProduct(${product.id})" 
                        style="color: var(--color-error);">Delete</button>
            </div>
        </div>
    `).join('');
}

// Profile Management
function loadProfile() {
    if (!appState.currentUser) return;
    
    const form = document.getElementById('profileForm');
    if (form) {
        form.querySelector('input[name="name"]').value = appState.currentUser.name || '';
        form.querySelector('input[name="email"]').value = appState.currentUser.email || '';
        form.querySelector('input[name="phone"]').value = appState.currentUser.phone || '';
        form.querySelector('textarea[name="address"]').value = appState.currentUser.address || '';
    }
}
