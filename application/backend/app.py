#!/usr/bin/env python3
"""
Currency Converter API Backend
Production-grade Flask API for currency conversion
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes (production should be more restrictive)
CORS(
    app,
    origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)


# Application configuration
class Config:
    """Application configuration"""

    API_VERSION = "1.0.0"
    SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "JPY"]

    # Hardcoded exchange rates (base: USD)
    # In production, these would come from an external service
    EXCHANGE_RATES = {
        "USD": {"USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0},
        "EUR": {"USD": 1.18, "EUR": 1.0, "GBP": 0.86, "JPY": 129.5},
        "GBP": {"USD": 1.37, "EUR": 1.16, "GBP": 1.0, "JPY": 150.7},
        "JPY": {"USD": 0.009, "EUR": 0.0077, "GBP": 0.0066, "JPY": 1.0},
    }


config = Config()


# Middleware for request logging
@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring"""
    logger.info("Health check requested")
    return (
        jsonify(
            {
                "status": "healthy",
                "message": "Currency converter API is running",
                "version": config.API_VERSION,
                "timestamp": datetime.utcnow().isoformat(),
                "supported_currencies": config.SUPPORTED_CURRENCIES,
            }
        ),
        200,
    )


# API info endpoint
@app.route("/api/info", methods=["GET"])
def api_info():
    """API information endpoint"""
    return (
        jsonify(
            {
                "name": "Currency Converter API",
                "version": config.API_VERSION,
                "endpoints": {
                    "health": "GET /health",
                    "convert": "POST /api/convert",
                    "rates": "GET /api/rates",
                },
                "supported_currencies": config.SUPPORTED_CURRENCIES,
            }
        ),
        200,
    )


# Get exchange rates endpoint
@app.route("/api/rates", methods=["GET"])
def get_rates():
    """Get all exchange rates"""
    base_currency = request.args.get("base", "USD").upper()

    if base_currency not in config.SUPPORTED_CURRENCIES:
        return (
            jsonify(
                {
                    "error": f"Unsupported base currency: {base_currency}",
                    "supported_currencies": config.SUPPORTED_CURRENCIES,
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "base_currency": base_currency,
                "rates": config.EXCHANGE_RATES[base_currency],
                "timestamp": datetime.utcnow().isoformat(),
            }
        ),
        200,
    )


# Currency conversion endpoint
@app.route("/api/convert", methods=["POST"])
def convert():
    """Convert currency amounts"""
    try:
        # Get JSON data from request
        data = request.get_json()
        logger.info(f"Conversion request: {data}")

        # Validate request data
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract and validate required fields
        amount = data.get("amount")
        from_currency = data.get("from", "").upper()
        to_currency = data.get("to", "").upper()

        # Validate amount
        if amount is None:
            return jsonify({"error": "Amount is required"}), 400

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return jsonify({"error": "Amount must be a valid number"}), 400

        if amount < 0:
            return jsonify({"error": "Amount must be positive"}), 400

        # Validate currencies
        if not from_currency or not to_currency:
            return jsonify({"error": "Both from and to currencies are required"}), 400

        if from_currency not in config.SUPPORTED_CURRENCIES:
            return (
                jsonify(
                    {
                        "error": f"Unsupported source currency: {from_currency}",
                        "supported_currencies": config.SUPPORTED_CURRENCIES,
                    }
                ),
                400,
            )

        if to_currency not in config.SUPPORTED_CURRENCIES:
            return (
                jsonify(
                    {
                        "error": f"Unsupported target currency: {to_currency}",
                        "supported_currencies": config.SUPPORTED_CURRENCIES,
                    }
                ),
                400,
            )

        # Get exchange rate
        exchange_rate = config.EXCHANGE_RATES[from_currency][to_currency]

        # Calculate converted amount
        converted_amount = round(amount * exchange_rate, 2)

        logger.info(
            f"Converted {amount} {from_currency} to {converted_amount} {to_currency}"
        )

        # Return conversion result
        return (
            jsonify(
                {
                    "success": True,
                    "original_amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "converted_amount": converted_amount,
                    "exchange_rate": exchange_rate,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred during conversion",
                }
            ),
            500,
        )


# Frontend serving routes (for containerized deployment)
@app.route("/")
def serve_frontend():
    """Serve the main frontend page"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return send_file(os.path.join(frontend_path, "index.html"))


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serve frontend assets (CSS, JS, etc.)"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return send_from_directory(os.path.join(frontend_path, "assets"), filename)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    # Check if this is an API request
    if request.path.startswith("/api/") or request.path.startswith("/health"):
        return (
            jsonify(
                {
                    "error": "Endpoint not found",
                    "message": "The requested endpoint does not exist",
                }
            ),
            404,
        )
    else:
        # For non-API requests, serve the frontend
        try:
            frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
            return send_file(os.path.join(frontend_path, "index.html"))
        except:
            return (
                jsonify(
                    {
                        "error": "Frontend not found",
                        "message": "Frontend files are not available",
                    }
                ),
                404,
            )


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return (
        jsonify(
            {
                "error": "Method not allowed",
                "message": f"The {request.method} method is not allowed for this endpoint",
            }
        ),
        405,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


if __name__ == "__main__":
    # Get port from environment variable or default to 8080
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting Currency Converter API on {host}:{port}")
    logger.info(f"API Version: {config.API_VERSION}")
    logger.info(f"Supported currencies: {config.SUPPORTED_CURRENCIES}")

    # Use debug mode only in development
    debug_mode = os.environ.get("FLASK_ENV", "production") != "production"
    app.run(host=host, port=port, debug=debug_mode)