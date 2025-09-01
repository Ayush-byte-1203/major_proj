/**
 * EcoScrap Application - Main Entry Point
 * 
 * This file serves as the main entry point for the EcoScrap application.
 * It exposes global functions that are used by HTML onclick handlers and
 * provides the bridge between the HTML interface and the modular JavaScript code.
 * 
 * Key Responsibilities:
 * - Expose global functions for HTML event handlers
 * - Provide access to core application functions
 * - Enable communication between HTML and JavaScript modules
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// GLOBAL FUNCTION EXPOSURE
// ========================================
// These functions are exposed globally to allow HTML onclick handlers to access them
// Each function delegates to the appropriate module for actual implementation

// Shopping Cart Functions
window.addToCart = addToCart;           // Add product to shopping cart
window.updateQuantity = updateQuantity; // Update product quantity in cart
window.removeFromCart = removeFromCart; // Remove product from cart
window.proceedToCheckout = proceedToCheckout; // Initiate checkout process

// User Management Functions (Admin Only)
window.toggleUserStatus = toggleUserStatus; // Toggle user active/blocked status
window.deleteUser = deleteUser;             // Delete user account
window.editUser = editUser;                 // Edit user information

// Product Management Functions (Admin/Dealer)
window.deleteProduct = deleteProduct;       // Delete product listing
window.approveProduct = approveProduct;     // Approve product for marketplace
window.rejectProduct = rejectProduct;       // Reject product listing

// System Management Functions
window.updateRate = updateRate;             // Update scrap material rates
window.closeModal = closeModal;             // Close modal dialogs
window.showSection = showSection;           // Navigate between application sections

/**
 * Note: The actual implementation of these functions is provided by the respective modules:
 * - Marketplace module: addToCart, updateQuantity, removeFromCart, proceedToCheckout
 * - Auth module: toggleUserStatus, deleteUser, editUser
 * - Dashboard module: deleteProduct, approveProduct, rejectProduct
 * - UI module: closeModal, showSection
 * - Content module: updateRate
 * 
 * This file acts as a facade, providing a clean interface for HTML elements to interact
 * with the modular JavaScript architecture.
 */
