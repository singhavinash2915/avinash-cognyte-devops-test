/**
 * API Service for Currency Converter Frontend
 * Handles all communication with the backend API
 */

class ApiService {
    constructor() {
        this.baseUrl = CONFIG.API.BASE_URL;
        this.timeout = CONFIG.API.TIMEOUT;
        this.retryConfig = CONFIG.API.RETRY;
    }

    /**
     * Make HTTP request with retry logic
     * @param {string} url - Request URL
     * @param {object} options - Fetch options
     * @param {number} attempt - Current attempt number
     * @returns {Promise<Response>}
     */
    async makeRequest(url, options = {}, attempt = 1) {
        try {
            // Add timeout to request
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    ...options.headers
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response;
            
        } catch (error) {
            if (attempt < this.retryConfig.MAX_ATTEMPTS && this.shouldRetry(error)) {
                this.log('warn', `Request failed (attempt ${attempt}/${this.retryConfig.MAX_ATTEMPTS}): ${error.message}`);
                
                // Exponential backoff
                const delay = this.retryConfig.DELAY * Math.pow(2, attempt - 1);
                await this.sleep(delay);
                
                return this.makeRequest(url, options, attempt + 1);
            }
            
            throw error;
        }
    }

    /**
     * Check if error should trigger a retry
     * @param {Error} error - Error object
     * @returns {boolean}
     */
    shouldRetry(error) {
        // Retry on network errors, timeouts, and 5xx server errors
        return error.name === 'AbortError' || 
               error.message.includes('fetch') ||
               error.message.includes('5');
    }

    /**
     * Sleep for specified duration
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Log messages with level
     * @param {string} level - Log level
     * @param {string} message - Log message
     */
    log(level, message) {
        if (CONFIG.ENV.DEBUG) {
            console[level](`[ApiService] ${message}`);
        }
    }

    /**
     * Check API health status
     * @returns {Promise<object>}
     */
    async checkHealth() {
        try {
            const url = ConfigUtils.getApiUrl('HEALTH');
            this.log('info', `Checking API health: ${url}`);
            
            const response = await this.makeRequest(url);
            const data = await response.json();
            
            this.log('info', 'API health check successful');
            return {
                success: true,
                data,
                status: 'healthy'
            };
            
        } catch (error) {
            this.log('error', `API health check failed: ${error.message}`);
            return {
                success: false,
                error: error.message,
                status: 'unhealthy'
            };
        }
    }

    /**
     * Convert currency
     * @param {object} conversionData - Conversion parameters
     * @returns {Promise<object>}
     */
    async convertCurrency(conversionData) {
        try {
            const { amount, from, to } = conversionData;
            
            // Validate input
            if (!amount || !from || !to) {
                throw new Error('Missing required conversion parameters');
            }
            
            if (isNaN(amount) || amount <= 0) {
                throw new Error('Amount must be a positive number');
            }
            
            if (from === to) {
                throw new Error('Source and target currencies must be different');
            }
            
            const url = ConfigUtils.getApiUrl('CONVERT');
            this.log('info', `Converting currency: ${amount} ${from} to ${to}`);
            
            const response = await this.makeRequest(url, {
                method: 'POST',
                body: JSON.stringify({
                    amount: parseFloat(amount),
                    from: from.toUpperCase(),
                    to: to.toUpperCase()
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Conversion failed');
            }
            
            this.log('info', `Conversion successful: ${data.converted_amount} ${data.to_currency}`);
            return {
                success: true,
                data
            };
            
        } catch (error) {
            this.log('error', `Currency conversion failed: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get exchange rates
     * @param {string} baseCurrency - Base currency for rates
     * @returns {Promise<object>}
     */
    async getExchangeRates(baseCurrency = 'USD') {
        try {
            const url = `${ConfigUtils.getApiUrl('RATES')}?base=${baseCurrency.toUpperCase()}`;
            this.log('info', `Fetching exchange rates for ${baseCurrency}`);
            
            const response = await this.makeRequest(url);
            const data = await response.json();
            
            this.log('info', 'Exchange rates fetched successfully');
            return {
                success: true,
                data
            };
            
        } catch (error) {
            this.log('error', `Failed to fetch exchange rates: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get API information
     * @returns {Promise<object>}
     */
    async getApiInfo() {
        try {
            const url = ConfigUtils.getApiUrl('INFO');
            this.log('info', 'Fetching API information');
            
            const response = await this.makeRequest(url);
            const data = await response.json();
            
            this.log('info', 'API information fetched successfully');
            return {
                success: true,
                data
            };
            
        } catch (error) {
            this.log('error', `Failed to fetch API info: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Create singleton instance
const apiService = new ApiService();