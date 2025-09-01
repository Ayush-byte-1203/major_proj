/**
 * EcoScrap Application - UI Module
 * 
 * This module provides essential user interface utilities and helper functions
 * for the EcoScrap application. It handles modal management, notification system,
 * form validation, and other UI-related functionality.
 * 
 * Key Features:
 * - Modal Management: Show/hide modal dialogs
 * - Notification System: Toast-style notifications with animations
 * - Form Validation: Comprehensive form validation with error handling
 * - Input Validation: Email, phone, and password validation
 * - Error Management: Field-level error display and clearing
 * 
 * UI Components:
 * - Modal dialogs for forms and content
 * - Toast notifications for user feedback
 * - Form validation with real-time error display
 * - Input sanitization and validation
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// MODAL MANAGEMENT
// ========================================
/**
 * Show a modal dialog by ID
 * Closes any existing modals and displays the requested modal
 * Prevents body scrolling when modal is active
 * 
 * @param {string} modalId - ID of the modal element to show
 */
function showModal(modalId) {
    console.log('Showing modal:', modalId);
    
    try {
        const modal = document.getElementById(modalId);
        if (modal) {
            // Close any existing modals first to prevent multiple open modals
            document.querySelectorAll('.modal').forEach(m => {
                m.classList.remove('active');
                m.classList.add('hidden');
            });
            
            // Show the requested modal and prevent body scrolling
            modal.classList.remove('hidden');
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            console.log('Modal shown successfully:', modalId);
        } else {
            console.error('Modal not found:', modalId);
        }
    } catch (error) {
        console.error('Error showing modal:', error);
    }
}

/**
 * Close all open modal dialogs
 * Restores body scrolling and clears any form errors
 * Ensures clean state for next modal interaction
 */
function closeModal() {
    try {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.remove('active');
            modal.classList.add('hidden');
            clearFormErrors(modal); // Clear any form errors when closing
        });
        document.body.style.overflow = 'auto'; // Restore body scrolling
    } catch (error) {
        console.error('Error closing modal:', error);
    }
}

// ========================================
// NOTIFICATION SYSTEM
// ========================================
/**
 * Display a toast-style notification to the user
 * Creates animated notifications with different types (success, error, warning, info)
 * Auto-dismisses after 5 seconds or can be manually closed
 * 
 * @param {string} message - Notification message to display
 * @param {string} type - Notification type: 'success', 'error', 'warning', 'info'
 */
function showNotification(message, type = 'info') {
    // Create notification element with appropriate styling
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    // Color scheme for different notification types
    const colors = {
        success: '#10b981', // Green for success messages
        error: '#ef4444',   // Red for error messages
        warning: '#f59e0b', // Orange for warning messages
        info: '#3b82f6'     // Blue for info messages
    };

    // Apply dynamic styling with animations
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        z-index: 3000;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        transform: translateX(100%);
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        max-width: 350px;
        backdrop-filter: blur(10px);
    `;

    // Add notification to DOM
    document.body.appendChild(notification);

    // Animate notification entrance
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto-remove notification after 5 seconds
    const removeNotification = () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 400);
    };

    // Set auto-dismiss timer and manual close handler
    setTimeout(removeNotification, 5000);
    notification.querySelector('.notification-close').onclick = removeNotification;
}

// ========================================
// FORM VALIDATION
// ========================================
/**
 * Validate a form and display appropriate error messages
 * Checks required fields, email format, password confirmation, and phone format
 * Returns boolean indicating if form is valid
 * 
 * @param {HTMLFormElement} form - Form element to validate
 * @returns {boolean} True if form is valid, false otherwise
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    // Validate each required input field
    inputs.forEach(input => {
        const value = input.value.trim();
        let errorMessage = '';
        
        // Check if field is empty
        if (!value) {
            errorMessage = `${input.previousElementSibling.textContent.replace('*', '').trim()} is required`;
            isValid = false;
        } else {
            // Validate specific field types
            if (input.type === 'email' && !isValidEmail(value)) {
                errorMessage = 'Please enter a valid email address';
                isValid = false;
            } else if (input.name === 'confirmPassword') {
                const password = form.querySelector('input[name="password"]').value;
                if (value !== password) {
                    errorMessage = 'Passwords do not match';
                    isValid = false;
                }
            } else if (input.name === 'phone' && !isValidPhone(value)) {
                errorMessage = 'Please enter a valid phone number';
                isValid = false;
            }
        }
        
        // Display or clear field error
        showFieldError(input, errorMessage);
    });
    
    return isValid;
}

/**
 * Validate email address format using regex
 * Checks for basic email structure: local@domain.tld
 * 
 * @param {string} email - Email address to validate
 * @returns {boolean} True if email format is valid
 */
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Validate phone number format
 * Accepts international format with optional + prefix
 * Allows 10-12 digits with optional spaces
 * 
 * @param {string} phone - Phone number to validate
 * @returns {boolean} True if phone format is valid
 */
function isValidPhone(phone) {
    return /^[+]?[0-9]{10,12}$/.test(phone.replace(/\s/g, ''));
}

/**
 * Display or hide field-level error messages
 * Shows error message below input field and applies error styling
 * 
 * @param {HTMLElement} input - Input element to show error for
 * @param {string} message - Error message to display (empty string to clear)
 */
function showFieldError(input, message) {
    const errorElement = input.parentElement.querySelector('.error-message');
    if (errorElement) {
        if (message) {
            // Show error message and apply error styling
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
            input.classList.add('error');
        } else {
            // Hide error message and remove error styling
            errorElement.classList.add('hidden');
            input.classList.remove('error');
        }
    }
}

/**
 * Clear all form errors in a container
 * Removes error styling and hides error messages
 * Useful when closing modals or resetting forms
 * 
 * @param {HTMLElement} container - Container element to clear errors from
 */
function clearFormErrors(container) {
    const errorElements = container.querySelectorAll('.error-message');
    const errorInputs = container.querySelectorAll('.error');
    
    // Hide all error messages
    errorElements.forEach(el => el.classList.add('hidden'));
    
    // Remove error styling from inputs
    errorInputs.forEach(input => input.classList.remove('error'));
}
