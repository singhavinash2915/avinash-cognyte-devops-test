/**
 * Configuration file for Currency Converter Frontend
 * Production-grade configuration management
 */

// Application configuration
const CONFIG = {
    // API Configuration
    API: {
        // Base URL for the backend API
        BASE_URL: window.location.origin,
        
        // API endpoints
        ENDPOINTS: {
            HEALTH: '/health',
            CONVERT: '/api/convert',
            RATES: '/api/rates',
            INFO: '/api/info'
        },
        
        // Request timeouts (in milliseconds)
        TIMEOUT: 10000,
        
        // Retry configuration
        RETRY: {
            MAX_ATTEMPTS: 3,
            DELAY: 1000 // Base delay between retries
        }
    },
    
    // Application settings
    APP: {
        NAME: 'Currency Converter',
        VERSION: '1.0.0',
        
        // Supported currencies
        CURRENCIES: ['USD', 'EUR', 'GBP', 'JPY'],
        
        // Default values
        DEFAULTS: {
            FROM_CURRENCY: 'USD',
            TO_CURRENCY: 'EUR',
            AMOUNT: '100'
        }
    },
    
    // UI Configuration
    UI: {
        // Animation durations (in milliseconds)
        ANIMATIONS: {
            FADE_DURATION: 300,
            SLIDE_DURATION: 500
        },
        
        // Health check interval (in milliseconds)
        HEALTH_CHECK_INTERVAL: 30000,
        
        // Auto-retry failed requests
        AUTO_RETRY: true
    },
    
    // Development/Production flags
    ENV: {
        DEBUG: true, // Set to false in production
        LOG_LEVEL: 'INFO' // DEBUG, INFO, WARN, ERROR
    }
};

// Currency metadata for enhanced UI
const CURRENCY_INFO = {
    USD: {
        name: 'US Dollar',
        symbol: '$',
        flag: '🇺🇸',
        decimals: 2
    },
    EUR: {
        name: 'Euro',
        symbol: '€',
        flag: '🇪🇺',
        decimals: 2
    },
    GBP: {
        name: 'British Pound',
        symbol: '£',
        flag: '🇬🇧',
        decimals: 2
    },
    JPY: {
        name: 'Japanese Yen',
        symbol: '¥',
        flag: '🇯🇵',
        decimals: 0
    }
};

// Utility functions for configuration
const ConfigUtils = {
    /**
     * Get full API endpoint URL
     * @param {string} endpoint - Endpoint key from CONFIG.API.ENDPOINTS
     * @returns {string} Full URL
     */
    getApiUrl: (endpoint) => {
        const baseUrl = CONFIG.API.BASE_URL.replace(/\/$/, ''); // Remove trailing slash
        const endpointPath = CONFIG.API.ENDPOINTS[endpoint.toUpperCase()];
        
        if (!endpointPath) {
            throw new Error(`Unknown endpoint: ${endpoint}`);
        }
        
        return `${baseUrl}${endpointPath}`;
    },
    
    /**
     * Check if debug mode is enabled
     * @returns {boolean}
     */
    isDebugMode: () => CONFIG.ENV.DEBUG,
    
    /**
     * Get currency information
     * @param {string} code - Currency code
     * @returns {object} Currency information
     */
    getCurrencyInfo: (code) => {
        return CURRENCY_INFO[code.toUpperCase()] || {
            name: code,
            symbol: code,
            flag: '💱',
            decimals: 2
        };
    },
    
    /**
     * Format amount according to currency
     * @param {number} amount - Amount to format
     * @param {string} currency - Currency code
     * @returns {string} Formatted amount
     */
    formatAmount: (amount, currency) => {
        const info = ConfigUtils.getCurrencyInfo(currency);
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: info.decimals,
            maximumFractionDigits: info.decimals
        }).format(amount);
    }
};

// Export configuration (for use in other modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, CURRENCY_INFO, ConfigUtils };
}