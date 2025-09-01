/**
 * EcoScrap Application - Database Module
 * 
 * This module provides a simulated database layer using localStorage for the EcoScrap application.
 * It handles all data persistence, retrieval, and management operations including users,
 * products, transactions, pickups, rates, tips, and shopping cart data.
 * 
 * Key Features:
 * - Local storage-based data persistence
 * - CRUD operations for all data entities
 * - Sample data initialization for demo purposes
 * - Data validation and error handling
 * - Automatic ID generation for new records
 * 
 * Data Entities:
 * - Users: Customer, Dealer, and Admin accounts
 * - Products: Recycled materials for sale
 * - Transactions: Order and payment records
 * - Pickups: Scrap collection scheduling
 * - Rates: Current market prices for materials
 * - Tips: Educational content for users
 * - Cart: Shopping cart items
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// DATABASE INTERFACE
// ========================================
/**
 * Database object that provides a unified interface for all data operations
 * Uses localStorage as the underlying storage mechanism
 */
const Database = {
    // ========================================
    // USER MANAGEMENT
    // ========================================
    /**
     * Retrieve all users from storage
     * @returns {Array} Array of user objects
     */
    getUsers: () => JSON.parse(localStorage.getItem('ecoscrap_users') || '[]'),
    
    /**
     * Save or update a user in storage
     * If user exists, updates the existing record; otherwise creates new
     * @param {Object} user - User object to save
     */
    saveUser: (user) => {
        const users = Database.getUsers();
        const existingIndex = users.findIndex(u => u.email === user.email);
        if (existingIndex >= 0) {
            users[existingIndex] = user;
        } else {
            users.push(user);
        }
        localStorage.setItem('ecoscrap_users', JSON.stringify(users));
    },
    
    /**
     * Delete a user by email address
     * @param {string} email - Email of user to delete
     */
    deleteUser: (email) => {
        const users = Database.getUsers();
        const filteredUsers = users.filter(u => u.email !== email);
        localStorage.setItem('ecoscrap_users', JSON.stringify(filteredUsers));
    },

    // ========================================
    // PRODUCT MANAGEMENT
    // ========================================
    /**
     * Retrieve all products from storage
     * @returns {Array} Array of product objects
     */
    getProducts: () => JSON.parse(localStorage.getItem('ecoscrap_products') || '[]'),
    
    /**
     * Save or update a product in storage
     * Generates unique ID and timestamp for new products
     * @param {Object} product - Product object to save
     * @returns {Object} Saved product with generated fields
     */
    saveProduct: (product) => {
        const products = Database.getProducts();
        const existingIndex = products.findIndex(p => p.id === product.id);
        if (existingIndex >= 0) {
            products[existingIndex] = product;
        } else {
            // Generate unique ID and timestamp for new products
            product.id = Date.now() + Math.random();
            product.createdAt = new Date().toISOString();
            products.push(product);
        }
        localStorage.setItem('ecoscrap_products', JSON.stringify(products));
        return product;
    },
    
    /**
     * Delete a product by ID
     * @param {string|number} productId - ID of product to delete
     */
    deleteProduct: (productId) => {
        const products = Database.getProducts();
        const filteredProducts = products.filter(p => p.id != productId);
        localStorage.setItem('ecoscrap_products', JSON.stringify(filteredProducts));
    },

    // ========================================
    // TRANSACTION MANAGEMENT
    // ========================================
    /**
     * Retrieve all transactions from storage
     * @returns {Array} Array of transaction objects
     */
    getTransactions: () => JSON.parse(localStorage.getItem('ecoscrap_transactions') || '[]'),
    
    /**
     * Save a new transaction with auto-generated ID and timestamp
     * @param {Object} transaction - Transaction object to save
     * @returns {Object} Saved transaction with generated fields
     */
    saveTransaction: (transaction) => {
        const transactions = Database.getTransactions();
        transaction.id = 'TXN' + Date.now();
        transaction.date = new Date().toISOString().split('T')[0];
        transaction.timestamp = new Date().toISOString();
        transactions.push(transaction);
        localStorage.setItem('ecoscrap_transactions', JSON.stringify(transactions));
        return transaction;
    },

    // ========================================
    // PICKUP MANAGEMENT
    // ========================================
    /**
     * Retrieve all pickup requests from storage
     * @returns {Array} Array of pickup objects
     */
    getPickups: () => JSON.parse(localStorage.getItem('ecoscrap_pickups') || '[]'),
    
    /**
     * Save a new pickup request with auto-generated ID and metadata
     * @param {Object} pickup - Pickup object to save
     * @returns {Object} Saved pickup with generated fields
     */
    savePickup: (pickup) => {
        const pickups = Database.getPickups();
        pickup.id = 'PU' + Date.now();
        pickup.bookedDate = new Date().toISOString().split('T')[0];
        pickup.status = 'scheduled';
        pickup.userEmail = appState.currentUser?.email;
        pickup.userName = appState.currentUser?.name;
        pickups.push(pickup);
        localStorage.setItem('ecoscrap_pickups', JSON.stringify(pickups));
        return pickup;
    },
    
    /**
     * Update an existing pickup request
     * @param {string} pickupId - ID of pickup to update
     * @param {Object} updates - Object containing fields to update
     */
    updatePickup: (pickupId, updates) => {
        const pickups = Database.getPickups();
        const index = pickups.findIndex(p => p.id === pickupId);
        if (index >= 0) {
            pickups[index] = { ...pickups[index], ...updates };
            localStorage.setItem('ecoscrap_pickups', JSON.stringify(pickups));
        }
    },

    // ========================================
    // RATES AND CONTENT MANAGEMENT
    // ========================================
    /**
     * Retrieve current scrap material rates
     * @returns {Array} Array of rate objects
     */
    getRates: () => JSON.parse(localStorage.getItem('ecoscrap_rates') || '[]'),
    
    /**
     * Save updated rates
     * @param {Array} rates - Array of rate objects to save
     */
    saveRates: (rates) => {
        localStorage.setItem('ecoscrap_rates', JSON.stringify(rates));
    },
    
    /**
     * Retrieve educational tips and guides
     * @returns {Array} Array of tip objects
     */
    getTips: () => JSON.parse(localStorage.getItem('ecoscrap_tips') || '[]'),
    
    /**
     * Save tips and guides
     * @param {Array} tips - Array of tip objects to save
     */
    saveTips: (tips) => {
        localStorage.setItem('ecoscrap_tips', JSON.stringify(tips));
    },

    // ========================================
    // SHOPPING CART MANAGEMENT
    // ========================================
    /**
     * Save shopping cart to storage
     * @param {Array} cart - Cart items array to save
     */
    saveCart: (cart) => {
        localStorage.setItem('ecoscrap_cart', JSON.stringify(cart));
    },
    
    /**
     * Retrieve shopping cart from storage
     * @returns {Array} Array of cart items
     */
    getCart: () => JSON.parse(localStorage.getItem('ecoscrap_cart') || '[]')
};

// ========================================
// SAMPLE DATA INITIALIZATION
// ========================================
/**
 * Sample data object containing demo users, rates, tips, and products
 * Used to populate the application with realistic data for demonstration
 */
const sampleData = {
    // ========================================
    // DEMO USERS
    // ========================================
    /**
     * Pre-configured demo user accounts for testing different roles
     * Includes admin, dealer, and customer accounts with realistic Indian context
     */
    demoUsers: [
        {
            email: "admin@ecoscrap.com",
            password: "admin123", 
            role: "admin",
            name: "Admin User",
            phone: "+91 9999999999",
            address: "EcoScrap HQ, Bandra Kurla Complex, Mumbai, Maharashtra 400051",
            status: "active",
            joinDate: "2024-01-15"
        },
        {
            email: "dealer1@ecoscrap.com",
            password: "dealer123",
            role: "dealer", 
            name: "Rajesh Kumar",
            phone: "+91 9876543210",
            address: "123 Industrial Area, Okhla Phase II, New Delhi 110020",
            status: "active",
            joinDate: "2024-02-20",
            businessName: "Kumar Metals & Recyclers"
        },
        {
            email: "dealer2@ecoscrap.com",
            password: "dealer123",
            role: "dealer", 
            name: "Sunita Singh",
            phone: "+91 9123456789",
            address: "456 Market Road, Hadapsar, Pune, Maharashtra 411028",
            status: "active",
            joinDate: "2024-03-10",
            businessName: "Singh Eco Solutions"
        },
        {
            email: "customer1@ecoscrap.com",
            password: "customer123",
            role: "customer",
            name: "Priya Sharma", 
            phone: "+91 8765432109",
            address: "789 Residential Colony, Koramangala, Bangalore, Karnataka 560095",
            status: "active",
            joinDate: "2024-02-25"
        },
        {
            email: "customer2@ecoscrap.com",
            password: "customer123",
            role: "customer",
            name: "Amit Patel", 
            phone: "+91 7654321098",
            address: "321 Sector 15, Gurugram, Haryana 122001",
            status: "active",
            joinDate: "2024-03-15"
        },
        {
            email: "dealer3@ecoscrap.com",
            password: "dealer123",
            role: "dealer",
            name: "Mohammed Ali",
            phone: "+91 8901234567",
            address: "567 Commercial Street, T. Nagar, Chennai, Tamil Nadu 600017",
            status: "active",
            joinDate: "2024-03-20",
            businessName: "Ali Scrap Trading Co."
        },
        {
            email: "customer3@ecoscrap.com",
            password: "customer123",
            role: "customer",
            name: "Kavya Nair",
            phone: "+91 9012345678",
            address: "890 Marine Drive, Ernakulam, Kochi, Kerala 682031",
            status: "active",
            joinDate: "2024-04-01"
        }
    ],

    // ========================================
    // CURRENT SCRAP RATES
    // ========================================
    /**
     * Current market rates for different scrap materials
     * Includes trend indicators and emoji icons for visual appeal
     * Rates are in Indian Rupees (₹) per kilogram
     */
    rates: [
        {material: "Aluminum", ratePerKg: 140, trend: "up", icon: "🥤"},
        {material: "Copper", ratePerKg: 650, trend: "up", icon: "🔌"},
        {material: "Steel", ratePerKg: 45, trend: "stable", icon: "🔩"},
        {material: "Brass", ratePerKg: 420, trend: "up", icon: "🔧"},
        {material: "Iron", ratePerKg: 35, trend: "stable", icon: "⚙️"},
        {material: "Plastic", ratePerKg: 25, trend: "down", icon: "♻️"},
        {material: "Cardboard", ratePerKg: 8, trend: "up", icon: "📦"},
        {material: "Newspaper", ratePerKg: 12, trend: "stable", icon: "📰"},
        {material: "Electronics", ratePerKg: 250, trend: "up", icon: "💾"}
    ],

    // ========================================
    // EDUCATIONAL TIPS AND GUIDES
    // ========================================
    /**
     * Educational content to help users maximize scrap value and practice safety
     * Organized by categories with impact indicators and visual icons
     */
    tips: [
        {
            id: 1,
            title: "Clean Your Metals Before Pickup",
            description: "Remove dirt, paint, and non-metal attachments from steel, aluminum, and copper to get better rates. Clean metals fetch 15-20% higher prices.",
            category: "Preparation",
            icon: "🧽",
            impact: "Higher Rates"
        },
        {
            id: 2, 
            title: "Separate Different Metal Types",
            description: "Don't mix aluminum with steel or copper. Different metals have different values. Copper is most valuable, then aluminum, then steel.",
            category: "Rates",
            icon: "🔧",
            impact: "Better Pricing"
        },
        {
            id: 3,
            title: "Remove Insulation from Copper Wires",
            description: "Stripped copper wire gets ₹650/kg while insulated wire gets only ₹250/kg. Spend time stripping for much better returns.",
            category: "Preparation", 
            icon: "⚡",
            impact: "160% More Value"
        },
        {
            id: 4,
            title: "Wear Safety Gloves and Shoes",
            description: "Always wear protective gear when handling scrap materials. Sharp edges, rust, and chemicals can cause injuries.",
            category: "Safety",
            icon: "🧤", 
            impact: "Stay Safe"
        },
        {
            id: 5,
            title: "Best Time to Sell Metals",
            description: "Metal prices are typically higher during construction season (March-September). Monitor trends and sell when rates are up.",
            category: "Rates",
            icon: "📈",
            impact: "Timing Matters"
        },
        {
            id: 6,
            title: "Identify Valuable Electronics",
            description: "Old computers, phones, and circuit boards contain precious metals. Don't throw them away - they can be worth ₹250-500/kg.",
            category: "Identification",
            icon: "💻",
            impact: "Hidden Value"
        },
        {
            id: 7,
            title: "Bundle Similar Materials",
            description: "Group newspapers together, cardboard separately. This saves time during pickup and ensures accurate weighing.",
            category: "Preparation",
            icon: "📦",
            impact: "Efficiency"
        },
        {
            id: 8,
            title: "Every Ton of Recycled Steel Saves 1.5 Tons of CO2",
            description: "Your contribution to recycling helps reduce greenhouse gases. Steel recycling is one of the most environmentally beneficial activities.",
            category: "Environment", 
            icon: "🌱",
            impact: "Save Planet"
        },
        {
            id: 9,
            title: "Store Materials in Dry Place",
            description: "Moisture can cause rust and reduce value of metals. Store your scrap in covered, dry areas to maintain quality.",
            category: "Storage",
            icon: "🏠",
            impact: "Preserve Value"
        },
        {
            id: 10,
            title: "Don't Break Glass or Ceramics",
            description: "Mixed broken glass is hard to sort and has low value. Keep bottles whole and separate by color when possible.",
            category: "Preparation",
            icon: "🍺",
            impact: "Better Handling"
        },
        {
            id: 11,
            title: "Check for Aluminum vs Steel with Magnet",
            description: "Use a magnet to identify metals. If it sticks, it's steel (₹45/kg). If not, it might be aluminum (₹140/kg) or copper (₹650/kg).",
            category: "Identification",
            icon: "🧲",
            impact: "Know Your Metals"
        },
        {
            id: 12,
            title: "Minimum Quantity for Free Pickup",
            description: "Most dealers require minimum 50kg for free pickup. Collect materials over time to reach minimum quantity and save pickup fees.",
            category: "Rates",
            icon: "⚖️", 
            impact: "Free Service"
        }
    ],

    // ========================================
    // SAMPLE PRODUCTS
    // ========================================
    /**
     * Sample recycled products available in the marketplace
     * Includes various categories with realistic pricing and dealer information
     */
    products: [
        {
            id: 1,
            dealerEmail: "dealer1@ecoscrap.com",
            dealerName: "Rajesh Kumar",
            name: "Recycled Steel Sheets",
            price: 3800,
            category: "metals",
            description: "High-quality recycled steel sheets perfect for construction. Tested for durability and strength.",
            status: "approved",
            stock: 50,
            rating: 4.5,
            image: "🔩"
        },
        {
            id: 2,
            dealerEmail: "dealer1@ecoscrap.com",
            dealerName: "Rajesh Kumar",
            name: "Copper Wire Scraps", 
            price: 10400,
            category: "metals",
            description: "Pure copper wire scraps with excellent conductivity. Ideal for electrical applications.",
            status: "approved",
            stock: 25,
            rating: 4.8,
            image: "🔌"
        },
        {
            id: 3,
            dealerEmail: "dealer2@ecoscrap.com",
            dealerName: "Sunita Singh",
            name: "Plastic Bottle Pellets",
            price: 1050,
            category: "plastics",
            description: "Clean PET plastic pellets ready for manufacturing. Food-grade quality available.",
            status: "approved",
            stock: 100,
            rating: 4.2,
            image: "♻️"
        },
        {
            id: 4,
            dealerEmail: "dealer2@ecoscrap.com",
            dealerName: "Sunita Singh",
            name: "Cardboard Sheets",
            price: 720,
            category: "paper",
            description: "Premium recycled cardboard sheets for packaging needs. Various thickness available.",
            status: "approved",
            stock: 200,
            rating: 4.0,
            image: "📦"
        },
        {
            id: 5,
            dealerEmail: "dealer3@ecoscrap.com",
            dealerName: "Mohammed Ali",
            name: "Aluminum Cans Bundle",
            price: 2700,
            category: "metals",
            description: "Clean aluminum cans ready for recycling. Sorted and compressed for easy handling.",
            status: "approved",
            stock: 75,
            rating: 4.1,
            image: "🥤"
        },
        {
            id: 6,
            dealerEmail: "dealer3@ecoscrap.com",
            dealerName: "Mohammed Ali",
            name: "Electronic Components",
            price: 15000,
            category: "electronics",
            description: "Mixed electronic components and circuit boards. Great for precious metal recovery.",
            status: "approved",
            stock: 30,
            rating: 4.6,
            image: "💾"
        },
        {
            id: 7,
            dealerEmail: "dealer1@ecoscrap.com",
            dealerName: "Rajesh Kumar",
            name: "Brass Fittings",
            price: 8900,
            category: "metals",
            description: "High-quality brass fittings and pipes. Perfect for plumbing and electrical work.",
            status: "approved",
            stock: 40,
            rating: 4.3,
            image: "🔧"
        }
    ]
};

// ========================================
// DATABASE INITIALIZATION
// ========================================
/**
 * Initialize the database with sample data if no data exists
 * This function runs once when the application starts to ensure
 * there is always data available for demonstration purposes
 */
function initializeDatabase() {
    try {
        // Initialize demo users if none exist
        const users = Database.getUsers();
        if (users.length === 0) {
            sampleData.demoUsers.forEach(user => Database.saveUser(user));
        }
        
        // Initialize rates if none exist
        const rates = Database.getRates();
        if (rates.length === 0) {
            Database.saveRates(sampleData.rates);
        }
        
        // Initialize tips if none exist
        const tips = Database.getTips();
        if (tips.length === 0) {
            Database.saveTips(sampleData.tips);
        }
        
        // Initialize sample products if none exist
        const products = Database.getProducts();
        if (products.length === 0) {
            sampleData.products.forEach(product => Database.saveProduct(product));
        }
        
        console.log('Database initialized successfully');
    } catch (error) {
        console.error('Error initializing database:', error);
    }
}
