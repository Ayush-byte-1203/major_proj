/**
 * EcoScrap Application - Core Application Logic
 * 
 * This file contains the core application logic, state management, and initialization
 * for the EcoScrap sustainable scrap marketplace application.
 * 
 * Key Responsibilities:
 * - Application state management
 * - Event listener setup and management
 * - Navigation and routing logic
 * - UI state updates and synchronization
 * - Section data loading and management
 * 
 * Architecture:
 * - Uses a centralized state object (appState) for application data
 * - Implements role-based access control for different user types
 * - Modular section loading system for dynamic content
 * - Event-driven architecture with centralized event handling
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// APPLICATION STATE MANAGEMENT
// ========================================
/**
 * Global application state object that maintains the current state of the application
 * This includes user authentication status, current section, cart data, and loading states
 */
let appState = {
    currentUser: null,        // Currently logged-in user object
    isLoggedIn: false,        // Authentication status flag
    cart: [],                 // Shopping cart items array
    currentSection: 'home',   // Currently active section/page
    isLoading: false          // Global loading state indicator
};

// ========================================
// APPLICATION INITIALIZATION
// ========================================
/**
 * Main application initialization - triggered when DOM is fully loaded
 * Sets up the application in the correct order: database → app → event listeners
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('EcoScrap Application Starting...');
    
    // Initialize immediately without delays for better performance
    initializeDatabase();  // Set up local storage and sample data
    initializeApp();       // Initialize application state and UI
    setupEventListeners(); // Set up all event handlers
    
    console.log('Application fully initialized');
});

/**
 * Initialize the application with saved user session and cart data
 * Restores user state from localStorage if available
 */
function initializeApp() {
    try {
        // Check for saved user session in localStorage
        const savedUser = localStorage.getItem('ecoscrap_current_user');
        if (savedUser) {
            try {
                appState.currentUser = JSON.parse(savedUser);
                appState.isLoggedIn = true;
            } catch (e) {
                // Clear corrupted user data
                localStorage.removeItem('ecoscrap_current_user');
                console.warn('Corrupted user data cleared');
            }
        }
        
        // Restore saved cart from localStorage
        appState.cart = Database.getCart();
        
        // Update UI to reflect current state
        updateUI();
        updateCartCount();
        showSection('home');
        
        console.log('App initialized successfully');
    } catch (error) {
        console.error('Error initializing app:', error);
    }
}

// ========================================
// EVENT LISTENER SETUP
// ========================================
/**
 * Set up all application event listeners
 * This includes navigation, forms, modals, and interactive elements
 */
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    try {
        // Brand logo navigation - return to home
        const navBrand = document.querySelector('.nav-brand');
        if (navBrand) {
            navBrand.addEventListener('click', function(e) {
                e.preventDefault();
                showSection('home');
            });
        }

        // Mobile menu toggle functionality
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', function(e) {
                e.preventDefault();
                navToggle.classList.toggle('active');
                navMenu.classList.toggle('active');
            });
        }

        // Authentication button event handlers
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const addUserBtn = document.getElementById('addUserBtn');
        
        if (loginBtn) {
            loginBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showModal('loginModal');
            });
        }
        
        if (registerBtn) {
            registerBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showModal('registerModal');
            });
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                logout();
            });
        }

        if (addUserBtn) {
            addUserBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showModal('addUserModal');
            });
        }

        // Navigation link event delegation for better performance
        document.addEventListener('click', function(e) {
            const navLink = e.target.closest('[data-section]');
            if (navLink) {
                e.preventDefault();
                const section = navLink.getAttribute('data-section');
                handleNavigation(section);
                closeMenu();
            }
        });

        // Set up form submission handlers
        setupFormHandlers();
        
        // Set up other interactive elements
        setupOtherListeners();
        
        console.log('Event listeners setup complete');
    } catch (error) {
        console.error('Error setting up event listeners:', error);
    }
}

/**
 * Set up form submission event handlers for all application forms
 * Maps form IDs to their respective handler functions
 */
function setupFormHandlers() {
    const forms = {
        'loginForm': handleLogin,           // User login
        'registerForm': handleRegister,     // User registration
        'addUserForm': handleAddUser,       // Admin user creation
        'profileForm': handleProfileUpdate, // Profile updates
        'quickPickupForm': handlePickupBooking, // Pickup scheduling
        'addProductForm': handleAddProduct, // Product creation
        'checkoutForm': handleCheckout      // Order completion
    };

    // Attach submit handlers to each form
    Object.keys(forms).forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', forms[formId]);
        }
    });
}

/**
 * Set up additional event listeners for interactive elements
 * Includes hero actions, modal controls, search, filters, and form interactions
 */
function setupOtherListeners() {
    // Hero section call-to-action buttons
    const heroBookPickup = document.getElementById('heroBookPickup');
    if (heroBookPickup) {
        heroBookPickup.addEventListener('click', function(e) {
            e.preventDefault();
            // Check if user is logged in and is a customer
            if (!appState.isLoggedIn || appState.currentUser.role !== 'customer') {
                showModal('loginModal');
                return;
            }
            // Scroll to pickup section
            const pickupSection = document.getElementById('pickupSection');
            if (pickupSection) {
                pickupSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // Modal close handlers - click outside or close button
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-close') || e.target.classList.contains('modal-overlay')) {
            closeModal();
        }
    });

    // Keyboard shortcuts - ESC key closes modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Search and filter functionality
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const categoryTipsFilter = document.getElementById('categoryTipsFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterProducts, 300));
    }
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterProducts);
    }
    if (categoryTipsFilter) {
        categoryTipsFilter.addEventListener('change', filterTips);
    }

    // Pickup form real-time calculations
    const materialSelect = document.querySelector('#quickPickupForm select[name="material"]');
    const weightInput = document.querySelector('#quickPickupForm input[name="weight"]');
    if (materialSelect) materialSelect.addEventListener('change', calculateEstimate);
    if (weightInput) weightInput.addEventListener('input', calculateEstimate);

    // Payment method change handler for checkout
    const paymentMethod = document.getElementById('paymentMethod');
    if (paymentMethod) {
        paymentMethod.addEventListener('change', handlePaymentMethodChange);
    }

    // Set minimum pickup date to tomorrow
    const pickupDateInput = document.querySelector('#quickPickupForm input[name="date"]');
    if (pickupDateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        pickupDateInput.min = tomorrow.toISOString().split('T')[0];
    }

    // Credit card number formatting
    setupCardFormatting();
}

// ========================================
// NAVIGATION AND ROUTING
// ========================================
/**
 * Handle navigation requests and enforce access control
 * Validates user permissions before allowing access to sections
 */
function handleNavigation(section) {
    console.log('Handling navigation to:', section);
    
    // Allow public sections for all users (guests and logged-in)
    if (!appState.isLoggedIn) {
        if (['home', 'rates', 'about'].includes(section)) {
            showSection(section);
        } else {
            // Redirect guests to login for protected sections
            showModal('loginModal');
        }
        return;
    }

    // Check role-based access for logged-in users
    const userRole = appState.currentUser.role;
    const allowedSections = getRoleAllowedSections(userRole);
    
    if (allowedSections.includes(section)) {
        showSection(section);
    } else {
        showNotification('Access denied for this section', 'error');
    }
}

/**
 * Get allowed sections based on user role
 * Implements role-based access control for different user types
 */
function getRoleAllowedSections(role) {
    const sections = {
        'customer': ['home', 'marketplace', 'cart', 'orders', 'pickups', 'rates', 'tips', 'profile'],
        'dealer': ['dashboard', 'my-products', 'add-product', 'dealer-orders', 'dealer-pickups', 'profile'],
        'admin': ['admin-dashboard', 'user-management', 'product-management', 'transactions', 'rates-management', 'profile']
    };
    return sections[role] || ['home'];
}

/**
 * Show a specific section and hide all others
 * Updates navigation state and loads section-specific data
 */
function showSection(sectionId) {
    console.log('Showing section:', sectionId);
    
    try {
        // Hide all sections immediately for better performance
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
            appState.currentSection = sectionId;
            updateActiveNavigation(sectionId);
            
            // Load section-specific data
            loadSectionData(sectionId);
            
            console.log('Successfully displayed section:', sectionId);
        } else {
            console.error('Section not found:', sectionId);
        }
    } catch (error) {
        console.error('Error showing section:', error);
    }
}

/**
 * Update navigation menu to reflect current active section
 * Highlights the current section in the navigation menu
 */
function updateActiveNavigation(sectionId) {
    // Remove active class from all navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current section link
    const activeLink = document.querySelector(`[data-section="${sectionId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

/**
 * Load section-specific data based on the current section
 * Delegates to appropriate data loading functions for each section
 */
function loadSectionData(sectionId) {
    try {
        switch(sectionId) {
            // Customer sections
            case 'home':
                loadHomeData();
                break;
            case 'marketplace':
                loadMarketplace();
                break;
            case 'cart':
                loadCart();
                break;
            case 'orders':
                loadCustomerOrders();
                break;
            case 'pickups':
                loadCustomerPickups();
                break;
            case 'rates':
                loadRates();
                break;
            case 'tips':
                loadTips();
                break;
            
            // Dealer sections
            case 'dashboard':
                loadDealerDashboard();
                break;
            case 'my-products':
                loadDealerProducts();
                break;
            case 'dealer-orders':
                loadDealerOrders();
                break;
            case 'dealer-pickups':
                loadDealerPickups();
                break;
            
            // Admin sections
            case 'admin-dashboard':
                loadAdminDashboard();
                break;
            case 'user-management':
                loadUserManagement();
                break;
            case 'product-management':
                loadProductManagement();
                break;
            case 'transactions':
                loadAllTransactions();
                break;
            case 'rates-management':
                loadRatesManagement();
                break;
            case 'profile':
                loadProfile();
                break;
            
            default:
                loadHomeData();
        }
    } catch (error) {
        console.error('Error loading section data:', error);
        showNotification('Error loading data', 'error');
    }
}

// ========================================
// UI STATE MANAGEMENT
// ========================================
/**
 * Update the user interface to reflect current application state
 * Handles user authentication display, navigation visibility, and user information
 */
function updateUI() {
    const userLoggedOut = document.querySelector('.user-logged-out');
    const userLoggedIn = document.querySelector('.user-logged-in');
    const userName = document.querySelector('.user-name');
    const userAvatar = document.querySelector('.user-avatar');
    const userRoleBadge = document.getElementById('userRoleBadge');

    if (appState.isLoggedIn && appState.currentUser) {
        // Show logged-in state
        if (userLoggedOut) userLoggedOut.classList.add('hidden');
        if (userLoggedIn) userLoggedIn.classList.remove('hidden');
        if (userName) userName.textContent = appState.currentUser.name;
        if (userAvatar) userAvatar.textContent = appState.currentUser.name.charAt(0).toUpperCase();
        if (userRoleBadge) userRoleBadge.textContent = appState.currentUser.role.toUpperCase();
        
        updateRoleBasedNavigation();
    } else {
        // Show guest state
        if (userLoggedOut) userLoggedOut.classList.remove('hidden');
        if (userLoggedIn) userLoggedIn.classList.add('hidden');
        
        showGuestNavigation();
    }
}

/**
 * Update navigation menu based on user role
 * Shows appropriate navigation items for the current user type
 */
function updateRoleBasedNavigation() {
    // Hide all navigation groups first
    document.querySelectorAll('.nav-group').forEach(group => {
        group.classList.add('hidden');
    });
    
    // Show navigation appropriate for the user's role
    const roleNavId = `${appState.currentUser.role}Nav`;
    const roleNav = document.getElementById(roleNavId);
    if (roleNav) {
        roleNav.classList.remove('hidden');
    } else {
        showGuestNavigation();
    }
}

/**
 * Show guest navigation menu
 * Displays public navigation items for unauthenticated users
 */
function showGuestNavigation() {
    document.querySelectorAll('.nav-group').forEach(group => {
        group.classList.add('hidden');
    });
    
    const guestNav = document.getElementById('guestNav');
    if (guestNav) {
        guestNav.classList.remove('hidden');
    }
}

/**
 * Close mobile navigation menu
 * Resets mobile menu state when navigation is complete
 */
function closeMenu() {
    const navMenu = document.getElementById('navMenu');
    const navToggle = document.getElementById('navToggle');
    
    if (navMenu) navMenu.classList.remove('active');
    if (navToggle) navToggle.classList.remove('active');
}

/**
 * Update shopping cart count display
 * Shows the total number of items in the user's cart
 */
function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    if (cartCount) {
        const totalItems = appState.cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
    }
}

// ========================================
// UTILITY FUNCTIONS
// ========================================
/**
 * Debounce function to limit the rate of function calls
 * Useful for search inputs and other frequent events
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Delay in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
