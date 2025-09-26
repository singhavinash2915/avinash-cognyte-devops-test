#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Currency Converter tests
"""

import pytest
import sys
import os

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, config


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def app_config():
    """Provide access to application configuration"""
    return config


@pytest.fixture
def sample_conversion_data():
    """Sample data for currency conversion tests"""
    return {
        'valid_conversion': {
            'amount': 100.0,
            'from': 'USD',
            'to': 'EUR'
        },
        'same_currency': {
            'amount': 50.0,
            'from': 'USD',
            'to': 'USD'
        },
        'decimal_amount': {
            'amount': 123.45,
            'from': 'GBP',
            'to': 'JPY'
        },
        'zero_amount': {
            'amount': 0.0,
            'from': 'EUR',
            'to': 'GBP'
        }
    }


@pytest.fixture
def invalid_conversion_data():
    """Invalid data for error testing"""
    return {
        'missing_amount': {
            'from': 'USD',
            'to': 'EUR'
        },
        'negative_amount': {
            'amount': -100.0,
            'from': 'USD',
            'to': 'EUR'
        },
        'invalid_amount': {
            'amount': 'not_a_number',
            'from': 'USD',
            'to': 'EUR'
        },
        'missing_from_currency': {
            'amount': 100.0,
            'to': 'EUR'
        },
        'missing_to_currency': {
            'amount': 100.0,
            'from': 'USD'
        },
        'unsupported_from_currency': {
            'amount': 100.0,
            'from': 'INR',
            'to': 'USD'
        },
        'unsupported_to_currency': {
            'amount': 100.0,
            'from': 'USD',
            'to': 'CAD'
        },
        'empty_currencies': {
            'amount': 100.0,
            'from': '',
            'to': ''
        }
    }