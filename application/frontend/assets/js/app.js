/**
 * Main Application Logic for Currency Converter Frontend
 * Production-grade JavaScript application
 */

class CurrencyConverterApp {
    constructor() {
        this.initialized = false;
        this.healthCheckInterval = null;
        
        // DOM elements
        this.elements = {
            form: null,
            amountInput: null,
            fromCurrencySelect: null,
            toCurrencySelect: null,
            convertBtn: null,
            swapBtn: null,
            resultSection: null,
            errorSection: null,
            loadingSection: null,
            apiStatus: null
        };
        
        // Application state
        this.state = {
            isLoading: false,
            apiHealthy: false,
            lastConversion: null
        };
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.initialized) return;
        
        try {
            this.log('info', 'Initializing Currency Converter App');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
                return;
            }
            
            // Initialize DOM elements
            this.initializeElements();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Set default values
            this.setDefaultValues();
            
            // Initial API health check
            await this.checkApiHealth();
            
            // Start periodic health checks
            this.startHealthCheck();
            
            this.initialized = true;
            this.log('info', 'Currency Converter App initialized successfully');
            
        } catch (error) {
            this.log('error', `Initialization failed: ${error.message}`);
            this.showError('Application initialization failed. Please refresh the page.');
        }
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        // Direct element mapping
        this.elements.form = document.getElementById('converterForm');
        this.elements.amountInput = document.getElementById('amount');
        this.elements.fromCurrencySelect = document.getElementById('fromCurrency');
        this.elements.toCurrencySelect = document.getElementById('toCurrency');
        this.elements.convertBtn = document.getElementById('convertBtn');
        this.elements.swapBtn = document.getElementById('swapBtn');
        this.elements.resultSection = document.getElementById('resultSection');
        this.elements.errorSection = document.getElementById('errorSection');
        this.elements.loadingSection = document.getElementById('loadingSection');
        this.elements.apiStatus = document.getElementById('apiStatus');
        
        // Check for required elements
        const requiredElements = [
            'amountInput', 'fromCurrencySelect', 'toCurrencySelect', 
            'convertBtn', 'swapBtn', 'apiStatus'
        ];
        
        for (const elementName of requiredElements) {
            if (!this.elements[elementName]) {
                throw new Error(`Required element not found: ${elementName}`);
            }
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Form submission
        this.elements.form?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleConversion();
        });
        
        // Convert button click
        this.elements.convertBtn?.addEventListener('click', () => {
            this.handleConversion();
        });
        
        // Swap currencies button
        this.elements.swapBtn?.addEventListener('click', () => {
            this.handleCurrencySwap();
        });
        
        // Input validation on change
        [this.elements.amountInput, this.elements.fromCurrencySelect, this.elements.toCurrencySelect]
            .forEach(element => {
                element?.addEventListener('change', () => this.validateForm());
                element?.addEventListener('input', () => this.validateForm());
            });
        
        // Enter key support for amount input
        this.elements.amountInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.validateForm()) {
                this.handleConversion();
            }
        });
        
        // Retry button in error section
        const retryBtn = document.getElementById('retryBtn');
        retryBtn?.addEventListener('click', () => {
            this.hideAllSections();
            this.handleConversion();
        });
        
        // Window focus event to check API health
        window.addEventListener('focus', () => {
            if (!this.state.apiHealthy) {
                this.checkApiHealth();
            }
        });
    }

    /**
     * Set default form values
     */
    setDefaultValues() {
        if (this.elements.fromCurrencySelect) {
            this.elements.fromCurrencySelect.value = CONFIG.APP.DEFAULTS.FROM_CURRENCY;
        }
        
        if (this.elements.toCurrencySelect) {
            this.elements.toCurrencySelect.value = CONFIG.APP.DEFAULTS.TO_CURRENCY;
        }
        
        if (this.elements.amountInput) {
            this.elements.amountInput.value = CONFIG.APP.DEFAULTS.AMOUNT;
        }
        
        this.validateForm();
    }

    /**
     * Validate form inputs
     * @returns {boolean} Form validity
     */
    validateForm() {
        const amount = parseFloat(this.elements.amountInput?.value || 0);
        const fromCurrency = this.elements.fromCurrencySelect?.value;
        const toCurrency = this.elements.toCurrencySelect?.value;
        
        const isValid = amount > 0 && fromCurrency && toCurrency && fromCurrency !== toCurrency;
        
        if (this.elements.convertBtn) {
            this.elements.convertBtn.disabled = !isValid || this.state.isLoading;
        }
        
        return isValid;
    }

    /**
     * Handle currency conversion
     */
    async handleConversion() {
        if (!this.validateForm() || this.state.isLoading) return;
        
        const conversionData = {
            amount: parseFloat(this.elements.amountInput.value),
            from: this.elements.fromCurrencySelect.value,
            to: this.elements.toCurrencySelect.value
        };
        
        this.log('info', 'Starting currency conversion', conversionData);
        
        try {
            this.setLoadingState(true);
            this.showLoadingSection();
            
            const result = await apiService.convertCurrency(conversionData);
            
            if (result.success) {
                this.state.lastConversion = result.data;
                this.showConversionResult(result.data);
            } else {
                this.showError(result.error || 'Conversion failed');
            }
            
        } catch (error) {
            this.log('error', 'Conversion error', error);
            this.showError('An unexpected error occurred during conversion');
        } finally {
            this.setLoadingState(false);
        }
    }

    /**
     * Handle currency swap
     */
    handleCurrencySwap() {
        const fromValue = this.elements.fromCurrencySelect.value;
        const toValue = this.elements.toCurrencySelect.value;
        
        this.elements.fromCurrencySelect.value = toValue;
        this.elements.toCurrencySelect.value = fromValue;
        
        this.validateForm();
        this.hideAllSections();
        
        this.log('info', `Currencies swapped: ${fromValue} ↔ ${toValue}`);
    }

    /**
     * Check API health
     */
    async checkApiHealth() {
        try {
            const result = await apiService.checkHealth();
            this.updateApiStatus(result.success, result.data);
        } catch (error) {
            this.updateApiStatus(false, { error: error.message });
        }
    }

    /**
     * Start periodic health checks
     */
    startHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        
        this.healthCheckInterval = setInterval(() => {
            this.checkApiHealth();
        }, CONFIG.UI.HEALTH_CHECK_INTERVAL);
    }

    /**
     * Update API status display
     * @param {boolean} healthy - API health status
     * @param {object} data - Health check data
     */
    updateApiStatus(healthy, data = {}) {
        this.state.apiHealthy = healthy;
        
        if (this.elements.apiStatus) {
            this.elements.apiStatus.textContent = healthy ? 'Connected' : 'Disconnected';
            this.elements.apiStatus.className = healthy ? 'status-healthy' : 'status-error';
        }
        
        this.log(healthy ? 'info' : 'warn', `API Status: ${healthy ? 'Healthy' : 'Unhealthy'}`, data);
    }

    /**
     * Set loading state
     * @param {boolean} loading - Loading state
     */
    setLoadingState(loading) {
        this.state.isLoading = loading;
        
        if (this.elements.convertBtn) {
            this.elements.convertBtn.disabled = loading || !this.validateForm();
            
            const buttonText = this.elements.convertBtn.querySelector('.button-text');
            const buttonLoading = this.elements.convertBtn.querySelector('.button-loading');
            
            if (buttonText && buttonLoading) {
                buttonText.style.display = loading ? 'none' : 'inline';
                buttonLoading.style.display = loading ? 'inline' : 'none';
            }
        }
    }

    /**
     * Show conversion result
     * @param {object} data - Conversion result data
     */
    showConversionResult(data) {
        this.hideAllSections();
        
        // Update result display
        const elements = {
            originalAmount: document.getElementById('originalAmount'),
            originalCurrency: document.getElementById('originalCurrency'),
            convertedAmount: document.getElementById('convertedAmount'),
            convertedCurrency: document.getElementById('convertedCurrency'),
            exchangeRate: document.getElementById('exchangeRate'),
            conversionTime: document.getElementById('conversionTime')
        };
        
        if (elements.originalAmount) {
            elements.originalAmount.textContent = ConfigUtils.formatAmount(data.original_amount, data.from_currency);
        }
        
        if (elements.originalCurrency) {
            const currencyInfo = ConfigUtils.getCurrencyInfo(data.from_currency);
            elements.originalCurrency.textContent = `${currencyInfo.flag} ${data.from_currency}`;
        }
        
        if (elements.convertedAmount) {
            elements.convertedAmount.textContent = ConfigUtils.formatAmount(data.converted_amount, data.to_currency);
        }
        
        if (elements.convertedCurrency) {
            const currencyInfo = ConfigUtils.getCurrencyInfo(data.to_currency);
            elements.convertedCurrency.textContent = `${currencyInfo.flag} ${data.to_currency}`;
        }
        
        if (elements.exchangeRate) {
            elements.exchangeRate.textContent = `1 ${data.from_currency} = ${data.exchange_rate} ${data.to_currency}`;
        }
        
        if (elements.conversionTime && data.timestamp) {
            const time = new Date(data.timestamp).toLocaleString();
            elements.conversionTime.textContent = time;
        }
        
        // Show result section
        if (this.elements.resultSection) {
            this.elements.resultSection.style.display = 'block';
        }
        
        this.log('info', 'Conversion result displayed successfully');
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.hideAllSections();
        
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        
        if (this.elements.errorSection) {
            this.elements.errorSection.style.display = 'block';
        }
        
        this.log('error', 'Error displayed to user', message);
    }

    /**
     * Show loading section
     */
    showLoadingSection() {
        this.hideAllSections();
        
        if (this.elements.loadingSection) {
            this.elements.loadingSection.style.display = 'block';
        }
    }

    /**
     * Hide all result sections
     */
    hideAllSections() {
        [this.elements.resultSection, this.elements.errorSection, this.elements.loadingSection]
            .forEach(section => {
                if (section) {
                    section.style.display = 'none';
                }
            });
    }

    /**
     * Log messages with level
     * @param {string} level - Log level
     * @param {string} message - Log message
     * @param {any} data - Additional data
     */
    log(level, message, data = null) {
        if (CONFIG.ENV.DEBUG) {
            const logMethod = console[level] || console.log;
            if (data) {
                logMethod(`[CurrencyConverterApp] ${message}`, data);
            } else {
                logMethod(`[CurrencyConverterApp] ${message}`);
            }
        }
    }

    /**
     * Cleanup method
     */
    destroy() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
        
        this.initialized = false;
        this.log('info', 'Currency Converter App destroyed');
    }
}

// Initialize the application
const app = new CurrencyConverterApp();

// Auto-initialize when script loads
app.init();

// Global error handler
window.addEventListener('error', (event) => {
    console.error('[Global Error Handler]', event.error);
    
    if (app && app.initialized) {
        app.showError('An unexpected error occurred. Please refresh the page.');
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('[Unhandled Promise Rejection]', event.reason);
    event.preventDefault();
    
    if (app && app.initialized) {
        app.showError('A network error occurred. Please check your connection and try again.');
    }
});