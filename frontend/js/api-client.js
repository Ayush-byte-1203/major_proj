/**
 * EcoScrap Application - API Client
 * 
 * This module provides a client-side API interface for communicating with
 * the Flask backend. It replaces the localStorage-based data management
 * with proper HTTP requests to the server.
 * 
 * Key Features:
 * - HTTP client for API communication with retry logic
 * - Authentication token management and session persistence
 * - Request/response handling with error management
 * - Automatic retry on network failures and server errors
 * - Session management using localStorage
 * - Comprehensive error handling with custom error classes
 * 
 * Architecture:
 * - RESTful API client with consistent interface
 * - Automatic authentication header management
 * - Request timeout and retry configuration
 * - Error classification and handling
 * - Response data transformation
 * 
 * API Endpoints Supported:
 * - Authentication: Login, logout, registration, profile management
 * - Products: CRUD operations, filtering, search
 * - Pickups: Scheduling, status updates, management
 * - Transactions: Order creation, history, management
 * - Rates: Current scrap material pricing
 * - Tips: Educational content with filtering
 * - Admin: User management, product approval
 * - Dashboard: Role-based statistics
 * 
 * Error Handling:
 * - Network timeout management (10 seconds)
 * - Automatic retry on 5xx server errors
 * - Custom error classes with status codes
 * - User-friendly error messages
 * - Graceful degradation on failures
 * 
 * Security Features:
 * - Secure token storage in localStorage
 * - Automatic token inclusion in requests
 * - Token cleanup on logout
 * - CORS-compliant request handling
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// API CLIENT CONFIGURATION
// ========================================
// Configuration object for the API client with network and retry settings

const API_CONFIG = {
    // Base URL for all API endpoints (Flask backend)
    BASE_URL: 'http://localhost:5001/api',
    
    // Request timeout in milliseconds (10 seconds)
    // Prevents requests from hanging indefinitely
    TIMEOUT: 10000,
    
    // Maximum number of retry attempts for failed requests
    // Retries are only attempted on network errors and 5xx server errors
    RETRY_ATTEMPTS: 3,
    
    // Delay between retry attempts in milliseconds (1 second)
    // Uses exponential backoff: 1s, 2s, 3s for successive retries
    RETRY_DELAY: 1000
};

// ========================================
// API CLIENT CLASS
// ========================================

class ApiClient {
    /**
     * Main API client class for communicating with the EcoScrap Flask backend
     * 
     * This class provides a comprehensive interface for all API operations
     * including authentication, data management, and error handling.
     * 
     * Features:
     * - Automatic authentication header management
     * - Request retry logic with exponential backoff
     * - Comprehensive error handling and classification
     * - Session persistence using localStorage
     * - Request timeout management
     * 
     * Usage:
     *     const apiClient = new ApiClient();
     *     const products = await apiClient.getProducts();
     *     const user = await apiClient.login({email: 'user@example.com', password: 'pass'});
     */
    constructor() {
        // Initialize configuration from API_CONFIG
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.retryAttempts = API_CONFIG.RETRY_ATTEMPTS;
        this.retryDelay = API_CONFIG.RETRY_DELAY;
        
        // Load authentication token from localStorage if available
        // This allows the client to maintain sessions across page reloads
        this.authToken = localStorage.getItem('ecoscrap_auth_token');
    }

    // ========================================
    // UTILITY METHODS
    // ========================================
    
    /**
     * Get authentication headers for requests
     * 
     * This method creates the appropriate headers for API requests,
     * including content type and authentication token if available.
     * 
     * Headers:
     * - Content-Type: application/json (for JSON request bodies)
     * - Authorization: Bearer token (if user is authenticated)
     * 
     * Security Features:
     * - Token is automatically included when available
     * - Prevents unauthorized access to protected endpoints
     * - Maintains session state across requests
     * 
     * @returns {Object} Headers object for fetch requests
     */
    getAuthHeaders() {
        // Set default headers for all requests
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Add authentication header if user is logged in
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }

    /**
     * Handle API response and extract data
     * 
     * This method processes the response from the server and handles
     * both successful responses and errors appropriately.
     * 
     * Response Handling:
     * - Successful responses (2xx): Returns parsed JSON data
     * - Error responses (4xx, 5xx): Throws ApiError with details
     * - Network errors: Propagated to calling method for retry logic
     * 
     * Error Classification:
     * - 4xx errors: Client errors (bad request, unauthorized, etc.)
     * - 5xx errors: Server errors (internal server error, etc.)
     * - Network errors: Connection issues, timeouts, etc.
     * 
     * @param {Response} response - Fetch API response object
     * @returns {Promise<Object>} Parsed JSON response data
     * @throws {ApiError} When response indicates an error
     */
    async handleResponse(response) {
        // Check if response indicates an error (non-2xx status codes)
        if (!response.ok) {
            // Try to extract error details from response body
            const errorData = await response.json().catch(() => ({}));
            
            // Create and throw a custom error with status and details
            throw new ApiError(
                response.status,
                errorData.error || `HTTP ${response.status}`,
                errorData
            );
        }
        
        // For successful responses, parse and return JSON data
        return response.json();
    }

    /**
     * Make HTTP request with retry logic
     * 
     * This is the core method that handles all HTTP requests to the API.
     * It includes automatic retry logic, timeout management, and error handling.
     * 
     * Retry Logic:
     * - Automatically retries failed requests up to RETRY_ATTEMPTS times
     * - Uses exponential backoff (1s, 2s, 3s delays)
     * - Only retries on network errors and 5xx server errors
     * - 4xx client errors are not retried (they won't succeed)
     * 
     * Timeout Management:
     * - Uses AbortSignal.timeout() for request timeout
     * - Prevents requests from hanging indefinitely
     * - Configurable timeout duration via API_CONFIG
     * 
     * Authentication:
     * - Automatically includes auth headers for all requests
     * - Maintains session state across requests
     * - Handles token expiration gracefully
     * 
     * @param {string} url - Full URL for the request
     * @param {Object} options - Fetch options (method, body, etc.)
     * @param {number} attempt - Current attempt number (for retry logic)
     * @returns {Promise<Object>} Parsed response data
     * @throws {Error} When all retry attempts are exhausted
     */
    async makeRequest(url, options, attempt = 1) {
        try {
            // Make the HTTP request with configured options
            const response = await fetch(url, {
                ...options,                                    // Spread user-provided options
                headers: this.getAuthHeaders(),               // Add auth headers automatically
                signal: AbortSignal.timeout(this.timeout)     // Set request timeout
            });
            
            // Process the response (success or error)
            return await this.handleResponse(response);
            
        } catch (error) {
            // Check if we should retry this request
            if (attempt < this.retryAttempts && this.shouldRetry(error)) {
                // Calculate delay with exponential backoff
                const delayTime = this.retryDelay * attempt;
                await this.delay(delayTime);
                
                // Retry the request with incremented attempt counter
                return this.makeRequest(url, options, attempt + 1);
            }
            
            // If we shouldn't retry or have exhausted attempts, throw the error
            throw error;
        }
    }

    /**
     * Determine if request should be retried
     */
    shouldRetry(error) {
        // Retry on network errors, timeouts, and 5xx server errors
        return error.name === 'AbortError' || 
               error.name === 'TypeError' ||
               (error.status >= 500 && error.status < 600);
    }

    /**
     * Delay execution for specified milliseconds
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ========================================
    // AUTHENTICATION METHODS
    // ========================================
    
    /**
     * User registration
     */
    async register(userData) {
        const response = await this.makeRequest(`${this.baseURL}/auth/register`, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        // Store auth token if provided
        if (response.token) {
            this.authToken = response.token;
            localStorage.setItem('ecoscrap_auth_token', this.authToken);
        }
        
        return response;
    }

    /**
     * User login
     * 
     * Authenticates a user with email and password credentials.
     * On successful login, stores the authentication token for future requests.
     * 
     * Authentication Flow:
     * 1. Send credentials to /api/auth/login endpoint
     * 2. Server validates credentials and returns user data with token
     * 3. Store authentication token in localStorage for persistence
     * 4. Set authToken for automatic inclusion in future requests
     * 
     * Security Features:
     * - Credentials are sent over HTTPS (in production)
     * - Token is stored securely in localStorage
     * - Token is automatically included in subsequent requests
     * - Session persists across page reloads and browser restarts
     * 
     * @param {Object} credentials - Login credentials
     * @param {string} credentials.email - User's email address
     * @param {string} credentials.password - User's password
     * @returns {Promise<Object>} Login response with user data and token
     * @throws {ApiError} When login fails (invalid credentials, account blocked, etc.)
     */
    async login(credentials) {
        // Send login request to authentication endpoint
        const response = await this.makeRequest(`${this.baseURL}/auth/login`, {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        // Store authentication token if provided in response
        if (response.token) {
            // Store token in memory for current session
            this.authToken = response.token;
            
            // Persist token in localStorage for session persistence
            localStorage.setItem('ecoscrap_auth_token', this.authToken);
        }
        
        return response;
    }

    /**
     * User logout
     * 
     * Logs out the current user by clearing authentication state
     * and notifying the server. This method ensures clean session termination.
     * 
     * Logout Process:
     * 1. Send logout request to server to invalidate server-side session
     * 2. Clear authentication token from memory
     * 3. Remove token from localStorage
     * 4. Ensure clean state regardless of server response
     * 
     * Security Features:
     * - Server-side session invalidation
     * - Complete token removal from client
     * - Clean state even if server request fails
     * - Prevents unauthorized access after logout
     * 
     * Error Handling:
     * - Uses try-finally to ensure token cleanup
     * - Token is always removed even if server request fails
     * - Graceful degradation on network issues
     * 
     * @returns {Promise<void>} Resolves when logout is complete
     * @throws {Error} Only if there's a critical system error
     */
    async logout() {
        try {
            // Notify server to invalidate session
            await this.makeRequest(`${this.baseURL}/auth/logout`, {
                method: 'POST'
            });
        } finally {
            // Always clear authentication state regardless of server response
            // This ensures clean logout even if server request fails
            this.authToken = null;
            localStorage.removeItem('ecoscrap_auth_token');
        }
    }

    /**
     * Get user profile
     */
    async getProfile() {
        return await this.makeRequest(`${this.baseURL}/auth/profile`, {
            method: 'GET'
        });
    }

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        return await this.makeRequest(`${this.baseURL}/auth/profile`, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    // ========================================
    // PRODUCT METHODS
    // ========================================
    // Methods for managing marketplace products including CRUD operations,
    // filtering, search, and approval workflow management
    
    /**
     * Get products with optional filtering
     * 
     * Retrieves products from the marketplace with support for various filters.
     * This method is used by customers to browse products and by dealers to
     * manage their listings.
     * 
     * Filtering Options:
     * - category: Filter by product category (metals, plastics, paper, electronics)
     * - search: Text search across product names and descriptions
     * - status: Filter by approval status (pending, approved, rejected)
     * 
     * Usage Examples:
     *     await apiClient.getProducts()                    // All products
     *     await apiClient.getProducts({category: 'metals'}) // Metals only
     *     await apiClient.getProducts({search: 'copper'})   // Search for copper
     *     await apiClient.getProducts({status: 'approved'}) // Approved products only
     * 
     * Business Logic:
     * - Customers see only approved products by default
     * - Dealers can see their own products regardless of status
     * - Admins can see all products with status filtering
     * 
     * @param {Object} filters - Optional filtering parameters
     * @param {string} filters.category - Product category filter
     * @param {string} filters.search - Text search filter
     * @param {string} filters.status - Approval status filter
     * @returns {Promise<Array>} Array of product objects
     * @throws {ApiError} When request fails or user unauthorized
     */
    async getProducts(filters = {}) {
        // Build query parameters for filtering
        const params = new URLSearchParams();
        
        // Add filters to query string if provided
        if (filters.category) params.append('category', filters.category);
        if (filters.search) params.append('search', filters.search);
        if (filters.status) params.append('status', filters.status);
        
        // Construct URL with query parameters
        const url = `${this.baseURL}/products${params.toString() ? '?' + params.toString() : ''}`;
        
        // Make GET request to products endpoint
        return await this.makeRequest(url, {
            method: 'GET'
        });
    }

    /**
     * Create new product (dealers only)
     * 
     * Allows dealers to create new product listings in the marketplace.
     * Products start with 'pending' status and require admin approval
     * before becoming visible to customers.
     * 
     * Product Creation Workflow:
     * 1. Dealer submits product details
     * 2. Product is created with 'pending' status
     * 3. Admin reviews and approves/rejects product
     * 4. Approved products appear in marketplace
     * 5. Rejected products are hidden with feedback
     * 
     * Required Fields:
     * - name: Product name/title
     * - price: Product price in Indian Rupees (₹)
     * - category: Product category (metals, plastics, paper, electronics)
     * - description: Detailed product description
     * - stock: Available quantity
     * 
     * Business Rules:
     * - Only dealers can create products
     * - Products require admin approval before sale
     * - Stock management is automatic
     * - Pricing follows market standards
     * 
     * @param {Object} productData - Product information
     * @param {string} productData.name - Product name
     * @param {number} productData.price - Product price
     * @param {string} productData.category - Product category
     * @param {string} productData.description - Product description
     * @param {number} productData.stock - Available stock quantity
     * @returns {Promise<Object>} Created product object
     * @throws {ApiError} When creation fails or user unauthorized
     */
    async createProduct(productData) {
        // Send POST request to create new product
        return await this.makeRequest(`${this.baseURL}/products`, {
            method: 'POST',
            body: JSON.stringify(productData)
        });
    }

    /**
     * Update product
     */
    async updateProduct(productId, productData) {
        return await this.makeRequest(`${this.baseURL}/products/${productId}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });
    }

    /**
     * Delete product
     */
    async deleteProduct(productId) {
        return await this.makeRequest(`${this.baseURL}/products/${productId}`, {
            method: 'DELETE'
        });
    }

    // ========================================
    // PICKUP METHODS
    // ========================================
    
    /**
     * Get pickups for current user
     */
    async getPickups() {
        return await this.makeRequest(`${this.baseURL}/pickups`, {
            method: 'GET'
        });
    }

    /**
     * Create new pickup request
     */
    async createPickup(pickupData) {
        return await this.makeRequest(`${this.baseURL}/pickups`, {
            method: 'POST',
            body: JSON.stringify(pickupData)
        });
    }

    /**
     * Update pickup status
     */
    async updatePickup(pickupId, updates) {
        return await this.makeRequest(`${this.baseURL}/pickups/${pickupId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    }

    // ========================================
    // TRANSACTION METHODS
    // ========================================
    
    /**
     * Get transactions for current user
     */
    async getTransactions() {
        return await this.makeRequest(`${this.baseURL}/transactions`, {
            method: 'GET'
        });
    }

    /**
     * Create new transaction/order
     */
    async createTransaction(transactionData) {
        return await this.makeRequest(`${this.baseURL}/transactions`, {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    // ========================================
    // RATES AND TIPS METHODS
    // ========================================
    
    /**
     * Get current scrap material rates
     */
    async getRates() {
        return await this.makeRequest(`${this.baseURL}/rates`, {
            method: 'GET'
        });
    }

    /**
     * Update rates (admins only)
     */
    async updateRates(ratesData) {
        return await this.makeRequest(`${this.baseURL}/rates`, {
            method: 'PUT',
            body: JSON.stringify(ratesData)
        });
    }

    /**
     * Get educational tips
     */
    async getTips(filters = {}) {
        const params = new URLSearchParams();
        if (filters.category) params.append('category', filters.category);
        
        const url = `${this.baseURL}/tips${params.toString() ? '?' + params.toString() : ''}`;
        
        return await this.makeRequest(url, {
            method: 'GET'
        });
    }

    // ========================================
    // DASHBOARD METHODS
    // ========================================
    
    /**
     * Get dashboard statistics
     */
    async getDashboardStats() {
        return await this.makeRequest(`${this.baseURL}/dashboard/stats`, {
            method: 'GET'
        });
    }

    // ========================================
    // ADMIN METHODS
    // ========================================
    
    /**
     * Get all users (admins only)
     */
    async getUsers() {
        return await this.makeRequest(`${this.baseURL}/admin/users`, {
            method: 'GET'
        });
    }

    /**
     * Update user (admins only)
     */
    async updateUser(userId, userData) {
        return await this.makeRequest(`${this.baseURL}/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    /**
     * Delete user (admins only)
     */
    async deleteUser(userId) {
        return await this.makeRequest(`${this.baseURL}/admin/users/${userId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Approve product (admins only)
     */
    async approveProduct(productId) {
        return await this.makeRequest(`${this.baseURL}/admin/products/${productId}/approve`, {
            method: 'POST'
        });
    }

    /**
     * Reject product (admins only)
     */
    async rejectProduct(productId) {
        return await this.makeRequest(`${this.baseURL}/admin/products/${productId}/reject`, {
            method: 'POST'
        });
    }

    // ========================================
    // UTILITY METHODS
    // ========================================
    
    /**
     * Calculate estimated value for scrap materials
     */
    async calculateEstimate(material, weight) {
        return await this.makeRequest(`${this.baseURL}/calculate-estimate`, {
            method: 'POST',
            body: JSON.stringify({ material, weight })
        });
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.authToken;
    }

    /**
     * Clear authentication
     */
    clearAuth() {
        this.authToken = null;
        localStorage.removeItem('ecoscrap_auth_token');
    }
}

// ========================================
// ERROR CLASSES
// ========================================

class ApiError extends Error {
    constructor(status, message, data = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

// ========================================
// GLOBAL API CLIENT INSTANCE
// ========================================

// Create global API client instance
const apiClient = new ApiClient();

// Export for use in other modules
window.apiClient = apiClient;
