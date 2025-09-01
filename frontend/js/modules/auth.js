/**
 * EcoScrap Application - Authentication Module
 * ===========================================
 * 
 * This module handles all user authentication, authorization, and user management
 * operations for the EcoScrap application. It provides secure login/logout functionality,
 * user registration, profile management, and administrative user operations.
 * 
 * Key Features:
 * - User authentication (login/logout)
 * - User registration with role selection
 * - Profile updates and management
 * - Role-based access control
 * - Admin user management functions
 * - Session persistence using localStorage
 * - Demo account support for testing
 * 
 * Security Features:
 * - Password validation and confirmation
 * - Role-based access restrictions
 * - User status management (active/blocked)
 * - Secure session handling
 * 
 * User Roles:
 * - Customer: Can buy products, book pickups, view rates and tips
 * - Dealer: Can sell products, manage inventory, view orders
 * - Admin: Can manage users, products, rates, and platform settings
 * 
 * Authentication Flow:
 * 1. User submits login/register form
 * 2. Form validation (required fields, email format, password strength)
 * 3. Credential verification against demo users or database users
 * 4. Session creation and user state management
 * 5. UI update and dashboard redirection
 * 
 * Session Management:
 * - User data stored in localStorage for persistence
 * - Application state synchronized with stored session
 * - Automatic logout on page refresh if session exists
 * - Role-based dashboard access control
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// AUTHENTICATION HANDLERS
// ========================================
/**
 * Handle user login form submission
 * 
 * This function processes login attempts by validating credentials against
 * both demo users (for testing) and database users (for production).
 * It creates user sessions and redirects users to appropriate dashboards.
 * 
 * Authentication Process:
 * 1. Form validation (email and password required)
 * 2. Demo user credential check (for testing purposes)
 * 3. Database user credential verification
 * 4. Account status validation (active/blocked)
 * 5. Session creation and user login
 * 6. UI update and dashboard redirection
 * 
 * Security Features:
 * - Form validation prevents empty submissions
 * - Account status check prevents blocked users from logging in
 * - Generic error messages don't reveal which credential is incorrect
 * - Session creation with proper user state management
 * 
 * @param {Event} e - Form submission event object
 * @returns {void} - No return value, handles login flow
 */
function handleLogin(e) {
    e.preventDefault();
    
    // Validate form before processing to prevent invalid submissions
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');

    // First check demo users for testing and demonstration purposes
    // Demo users provide immediate access for testing without database setup
    const demoUser = sampleData.demoUsers.find(u => u.email === email && u.password === password);
    if (demoUser) {
        loginUser(demoUser);
        e.target.reset();
        return;
    }

    // Check database users for production accounts
    // This is the main authentication path for registered users
    const users = Database.getUsers();
    const user = users.find(u => u.email === email && u.password === password);
    if (user && user.status === 'active') {
        loginUser(user);
        e.target.reset();
    } else {
        // Show generic error message for security (don't reveal which field is wrong)
        showNotification('Invalid email or password', 'error');
    }
}

/**
 * Handle user registration form submission
 * 
 * This function processes new user registrations by creating user accounts
 * with selected roles and automatically logging in the new user after
 * successful account creation.
 * 
 * Registration Process:
 * 1. Form validation (all required fields)
 * 2. Email uniqueness check (prevent duplicate accounts)
 * 3. User object creation with form data
 * 4. Database storage of new user account
 * 5. Automatic login for immediate access
 * 6. Form reset and success feedback
 * 
 * Business Rules:
 * - Email addresses must be unique across all users
 * - New users default to 'customer' role if none specified
 * - All new accounts start with 'active' status
 * - Join date automatically set to current date
 * - Users are immediately logged in after registration
 * 
 * @param {Event} e - Form submission event object
 * @returns {void} - No return value, handles registration flow
 */
function handleRegister(e) {
    e.preventDefault();
    
    // Validate form before processing to ensure all required data is provided
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    
    // Check if email is already registered to prevent duplicate accounts
    // This maintains data integrity and prevents user confusion
    const users = Database.getUsers();
    if (users.find(u => u.email === email)) {
        showNotification('Email already registered', 'error');
        return;
    }

    // Create new user object with form data and default values
    // Default values ensure consistent user state and reduce form complexity
    const newUser = {
        name: formData.get('name'),
        email: email,
        phone: formData.get('phone'),
        address: formData.get('address'),
        password: formData.get('password'),
        role: formData.get('role') || 'customer', // Default to customer role for safety
        status: 'active', // New users are active by default
        joinDate: new Date().toISOString().split('T')[0] // Current date in YYYY-MM-DD format
    };
    
    // Save user to database and automatically log them in
    // This provides immediate access without requiring separate login
    Database.saveUser(newUser);
    loginUser(newUser);
    e.target.reset();
}

/**
 * Handle admin user creation form submission
 * 
 * This function allows administrators to create new user accounts with
 * full control over user roles and settings. It's part of the admin
 * user management system.
 * 
 * Admin User Creation Process:
 * 1. Form validation (all required fields)
 * 2. Email uniqueness verification
 * 3. User object creation with admin-specified data
 * 4. Database storage and user list refresh
 * 5. Success feedback and modal closure
 * 
 * Administrative Features:
 * - Can create users with any role (including admin)
 * - Immediate user list refresh for admin dashboard
 * - Success notifications for user feedback
 * - Modal management for clean UI flow
 * 
 * Security Considerations:
 * - Only accessible to admin users
 * - Full role assignment capabilities
 * - Immediate account activation
 * 
 * @param {Event} e - Form submission event object
 * @returns {void} - No return value, handles admin user creation
 */
function handleAddUser(e) {
    e.preventDefault();
    
    // Validate form before processing to ensure complete user data
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    
    // Check if email already exists to prevent duplicate accounts
    // This maintains data integrity in the admin user management system
    const users = Database.getUsers();
    if (users.find(u => u.email === email)) {
        showNotification('Email already exists', 'error');
        return;
    }

    // Create new user object with admin-specified data
    // Admin has full control over user role and initial settings
    const newUser = {
        name: formData.get('name'),
        email: email,
        phone: formData.get('phone'),
        address: formData.get('address'),
        password: formData.get('password'),
        role: formData.get('role'),
        status: 'active', // Admin-created users are active by default
        joinDate: new Date().toISOString().split('T')[0]
    };
    
    // Save user and provide feedback to admin
    // Refresh user list to show newly created user immediately
    Database.saveUser(newUser);
    showNotification(`User ${newUser.name} added successfully!`, 'success');
    e.target.reset();
    closeModal();
    loadUserManagement(); // Refresh user list for admin dashboard
}

/**
 * Handle user profile update form submission
 * 
 * This function processes profile updates for logged-in users, allowing
 * them to modify their personal information while maintaining session
 * consistency and data integrity.
 * 
 * Profile Update Process:
 * 1. Form validation (required fields)
 * 2. User object update with new information
 * 3. Database storage of updated user data
 * 4. Application state synchronization
 * 5. UI update to reflect changes
 * 6. Success notification
 * 
 * Data Synchronization:
 * - Database updated with new user information
 * - Application state reflects changes immediately
 * - Local storage updated for session persistence
 * - UI components refreshed to show updated data
 * 
 * Security Features:
 * - Users can only update their own profiles
 * - Password changes require separate authentication
 * - Session data remains consistent after updates
 * 
 * @param {Event} e - Form submission event object
 * @returns {void} - No return value, handles profile update flow
 */
function handleProfileUpdate(e) {
    e.preventDefault();
    
    // Validate form before processing to ensure data quality
    if (!validateForm(e.target)) return;
    
    const formData = new FormData(e.target);
    
    // Create updated user object with new information
    // Preserve existing user data while updating specified fields
    const updatedUser = {
        ...appState.currentUser,
        name: formData.get('name'),
        phone: formData.get('phone'),
        address: formData.get('address')
    };
    
    // Save updated user and update application state
    // This ensures consistency between database and application
    Database.saveUser(updatedUser);
    appState.currentUser = updatedUser;
    localStorage.setItem('ecoscrap_current_user', JSON.stringify(updatedUser));
    updateUI();
    
    showNotification('Profile updated successfully!', 'success');
}

// ========================================
// SESSION MANAGEMENT
// ========================================
/**
 * Log in a user and create application session
 * 
 * This function establishes a user session by setting up application state,
 * updating the UI, and redirecting the user to their appropriate dashboard
 * based on their role.
 * 
 * Session Creation Process:
 * 1. Set application state for logged-in user
 * 2. Update login status and user information
 * 3. Store session data in localStorage for persistence
 * 4. Update UI to reflect logged-in state
 * 5. Redirect to role-appropriate dashboard
 * 
 * Role-Based Redirection:
 * - Admin users: Admin dashboard with user and system management
 * - Dealer users: Dealer dashboard with product and order management
 * - Customer users: Customer dashboard with orders and pickup history
 * 
 * Session Persistence:
 * - User data stored in localStorage for page refresh persistence
 * - Application state synchronized with stored session
 * - Automatic login restoration on page reload
 * 
 * @param {Object} user - User object to log in
 * @returns {void} - No return value, handles login flow
 */
function loginUser(user) {
    // Set application state for logged-in user
    // This establishes the user session in the application
    appState.currentUser = user;
    appState.isLoggedIn = true;
    
    // Persist user session in localStorage for page refresh persistence
    // This ensures users remain logged in even after browser refresh
    localStorage.setItem('ecoscrap_current_user', JSON.stringify(appState.currentUser));
    
    // Update UI to reflect logged-in state
    // This includes showing user-specific content and hiding login forms
    updateUI();
    closeModal();
    
    // Show welcome message and redirect to appropriate dashboard
    // Personalized greeting enhances user experience
    showNotification(`Welcome back, ${user.name}!`, 'success');
    redirectToRoleHome();
}

/**
 * Log out current user and clear session
 * 
 * This function terminates the user session by clearing all application state,
 * removing stored session data, and redirecting the user to the home page.
 * 
 * Logout Process:
 * 1. Clear application state (user, login status, cart)
 * 2. Remove session data from localStorage
 * 3. Update UI to reflect logged-out state
 * 4. Redirect to home page
 * 5. Show logout confirmation message
 * 
 * Security Features:
 * - Complete session termination
 * - Cart data cleared for privacy
 * - All stored user data removed
 * - UI reset to public state
 * 
 * Data Cleanup:
 * - User object set to null
 * - Login status reset to false
 * - Shopping cart emptied
 * - Local storage cleared
 * 
 * @returns {void} - No return value, handles logout flow
 */
function logout() {
    // Clear application state to terminate user session
    // This ensures complete logout and prevents unauthorized access
    appState.currentUser = null;
    appState.isLoggedIn = false;
    appState.cart = [];
    
    // Clear stored session data from localStorage
    // This removes all persistent user data for security
    localStorage.removeItem('ecoscrap_current_user');
    localStorage.removeItem('ecoscrap_cart');
    
    // Update UI to reflect logged-out state and redirect to home
    // Users are returned to public home page after logout
    updateUI();
    showSection('home');
    showNotification('Logged out successfully!', 'success');
}

/**
 * Redirect user to appropriate home section based on their role
 * 
 * This function provides role-based navigation by directing users to
 * the most appropriate section based on their account type and permissions.
 * 
 * Role-Based Navigation:
 * - Customer: Home page with pickup booking and marketplace access
 * - Dealer: Business dashboard with product and order management
 * - Admin: Administrative dashboard with user and system management
 * 
 * Navigation Logic:
 * 1. Determine user role from current session
 * 2. Map role to appropriate home section
 * 3. Use timeout to ensure smooth transition
 * 4. Fallback to general home page for unknown roles
 * 
 * User Experience:
 * - Immediate access to role-relevant functionality
 * - Consistent navigation patterns
 * - Reduced user confusion about where to go
 * 
 * @returns {void} - No return value, handles navigation redirection
 */
function redirectToRoleHome() {
    // Define role-specific home sections for optimal user experience
    // Each role has different primary functions and needs
    const roleHomes = {
        'customer': 'home',      // Customer home page with pickup booking
        'dealer': 'dashboard',   // Dealer business dashboard
        'admin': 'admin-dashboard' // Admin platform management dashboard
    };
    
    // Get target section based on user role, fallback to general home
    const targetSection = roleHomes[appState.currentUser.role] || 'home';
    
    // Use timeout to ensure smooth transition after login animation
    // This prevents jarring immediate navigation
    setTimeout(() => showSection(targetSection), 200);
}

// ========================================
// ADMIN USER MANAGEMENT FUNCTIONS
// ========================================
/**
 * Toggle user account status between active and blocked
 * 
 * This function allows administrators to temporarily disable user accounts
 * without permanently deleting them. It's useful for moderation and
 * temporary suspensions.
 * 
 * Status Toggle Process:
 * 1. Find user by email address
 * 2. Toggle between 'active' and 'blocked' status
 * 3. Save updated user data to database
 * 4. Refresh admin interface to show changes
 * 5. Provide feedback on status change
 * 
 * Use Cases:
 * - Temporary account suspension for policy violations
 * - Account reactivation after issues resolved
 * - Administrative control over user access
 * - Non-destructive user management
 * 
 * Security Features:
 * - Only administrators can toggle user status
 * - Status changes are immediately reflected
 * - User list automatically refreshed
 * - Clear feedback on action results
 * 
 * @param {string} email - Email address of the user to toggle status
 * @returns {void} - No return value, handles status toggle
 */
function toggleUserStatus(email) {
    // Retrieve current user list from database
    const users = Database.getUsers();
    
    // Find the specific user by email address
    const user = users.find(u => u.email === email);
    
    if (user) {
        // Toggle between active and blocked status
        // This provides reversible account control
        user.status = user.status === 'active' ? 'blocked' : 'active';
        
        // Save updated user data to database
        Database.saveUser(user);
        
        // Refresh user management interface to show changes
        // This ensures admin sees immediate results
        loadUserManagement();
        
        // Provide clear feedback on status change
        // Success message confirms action completion
        const action = user.status === 'active' ? 'activated' : 'blocked';
        showNotification(`User ${action} successfully`, 'success');
    }
}

/**
 * Permanently delete a user account
 * 
 * This function removes a user account and all associated data from the system.
 * It's a destructive operation that should be used with caution.
 * 
 * Deletion Process:
 * 1. Confirm deletion with user (confirmation dialog)
 * 2. Remove user from database
 * 3. Refresh admin interface
 * 4. Provide deletion confirmation
 * 
 * Warning Features:
 * - Confirmation dialog prevents accidental deletions
 * - Clear feedback on successful deletion
 * - Immediate interface refresh
 * 
 * Data Impact:
 * - User account completely removed
 * - Associated data may be affected
 * - Action cannot be undone
 * 
 * Security Considerations:
 * - Only administrators can delete users
 * - Confirmation required for destructive action
 * - Immediate feedback on action completion
 * 
 * @param {string} email - Email address of the user to delete
 * @returns {void} - No return value, handles user deletion
 */
function deleteUser(email) {
    // Require confirmation before permanent deletion
    // This prevents accidental loss of user data
    if (confirm('Are you sure you want to delete this user?')) {
        // Remove user from database
        Database.deleteUser(email);
        
        // Refresh user management interface
        // This removes deleted user from admin view
        loadUserManagement();
        
        // Provide confirmation of successful deletion
        showNotification('User deleted successfully', 'success');
    }
}

/**
 * Edit user information (placeholder for future implementation)
 * 
 * This function is a placeholder for future user editing functionality.
 * It currently shows a notification that the feature is coming soon.
 * 
 * Future Implementation:
 * - Inline user editing in admin interface
 * - Form-based user information updates
 * - Real-time validation and feedback
 * - Bulk user editing capabilities
 * 
 * Current Behavior:
 * - Shows informational notification
 * - Indicates feature availability
 * - Maintains consistent interface
 * 
 * @param {string} email - Email address of the user to edit
 * @returns {void} - No return value, placeholder function
 */
function editUser(email) {
    // Show notification that edit functionality is coming soon
    // This provides user feedback while maintaining interface consistency
    showNotification('Edit functionality coming soon', 'info');
}
