/**
 * EcoScrap Application - Content Module
 * 
 * This module handles the display and management of static content throughout
 * the EcoScrap application. It manages rates display, educational tips, and
 * home page content rendering.
 * 
 * Key Features:
 * - Home Page Content: Rates display and featured content
 * - Rates Management: Current scrap material prices with trends
 * - Tips and Guides: Educational content with category filtering
 * - Content Rendering: Dynamic HTML generation from data
 * - Filtering System: Category-based content filtering
 * 
 * Content Types:
 * - Scrap Material Rates: Current market prices with trend indicators
 * - Educational Tips: Best practices for scrap management
 * - Category-based Content: Organized content by material type
 * 
 * @author EcoScrap Development Team
 * @version 1.0.0
 * @since 2024
 */

// ========================================
// HOME PAGE CONTENT
// ========================================
/**
 * Load and display home page content
 * Shows featured rates (first 6) on the home page
 * Provides quick overview of current market conditions
 */
function loadHomeData() {
    const ratesGrid = document.getElementById('homeRatesGrid');
    if (!ratesGrid) return;

    // Get current rates from database
    const rates = Database.getRates();
    
    // Display first 6 rates as featured content on home page
    ratesGrid.innerHTML = rates.slice(0, 6).map(rate => `
        <div class="rate-card">
            <div class="rate-icon">${rate.icon}</div>
            <h3 class="rate-material">${rate.material}</h3>
            <div class="rate-price">₹${rate.ratePerKg}/kg</div>
            <div class="status status--${rate.trend === 'up' ? 'success' : rate.trend === 'down' ? 'error' : 'info'}">
                ${rate.trend === 'up' ? '↗ Up' : rate.trend === 'down' ? '↘ Down' : '→ Stable'}
            </div>
        </div>
    `).join('');
}

// ========================================
// RATES MANAGEMENT
// ========================================
/**
 * Load and display all current scrap material rates
 * Shows complete rates table with trend indicators
 * Used in dedicated rates section for detailed viewing
 */
function loadRates() {
    const ratesGrid = document.getElementById('ratesGrid');
    if (!ratesGrid) return;

    // Get all rates from database
    const rates = Database.getRates();
    
    // Display all rates with trend indicators
    ratesGrid.innerHTML = rates.map(rate => `
        <div class="rate-card">
            <div class="rate-icon">${rate.icon}</div>
            <h3 class="rate-material">${rate.material}</h3>
            <div class="rate-price">₹${rate.ratePerKg}/kg</div>
            <div class="status status--${rate.trend === 'up' ? 'success' : rate.trend === 'down' ? 'error' : 'info'}">
                ${rate.trend === 'up' ? '↗ Up' : rate.trend === 'down' ? '↘ Down' : '→ Stable'}
            </div>
        </div>
    `).join('');
}

// ========================================
// TIPS AND GUIDES MANAGEMENT
// ========================================
/**
 * Load and display educational tips and guides
 * Shows tips organized by category with visual indicators
 * Provides valuable information for users to maximize scrap value
 */
function loadTips() {
    const tipsGrid = document.getElementById('tipsGrid');
    if (!tipsGrid) return;

    // Get tips from database
    const tips = Database.getTips();
    
    // Handle empty state if no tips available
    if (tips.length === 0) {
        tipsGrid.innerHTML = '<div class="empty-state">No tips available at the moment.</div>';
        return;
    }

    // Display tips with category badges and impact indicators
    tipsGrid.innerHTML = tips.map(tip => `
        <div class="tip-card" data-category="${tip.category}">
            <div class="tip-header">
                <div class="tip-icon">${tip.icon}</div>
                <div class="tip-category-badge">${tip.category}</div>
            </div>
            <h3 class="tip-title">${tip.title}</h3>
            <p class="tip-description">${tip.description}</p>
            <div class="tip-impact">${tip.impact}</div>
        </div>
    `).join('');
}

/**
 * Filter tips by category selection
 * Shows/hides tip cards based on selected category filter
 * Provides dynamic content filtering for better user experience
 */
function filterTips() {
    // Get selected category from filter dropdown
    const categoryFilter = document.getElementById('categoryTipsFilter')?.value || '';
    const tipCards = document.querySelectorAll('.tip-card');
    
    // Filter tip cards based on category selection
    tipCards.forEach(card => {
        const category = card.getAttribute('data-category') || '';
        
        // Show card if it matches selected category or if no category is selected
        const matchesCategory = !categoryFilter || category === categoryFilter;
        
        if (matchesCategory) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}
