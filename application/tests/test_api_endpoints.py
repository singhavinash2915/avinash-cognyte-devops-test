#!/usr/bin/env python3
"""
Unit tests for additional API endpoints (/api/rates, /api/info)
"""

import pytest
import json
from datetime import datetime


@pytest.mark.unit
@pytest.mark.api
class TestRatesEndpoint:
    """Test cases for the /api/rates endpoint"""
    
    def test_rates_endpoint_default_base_currency(self, client, app_config):
        """Test rates endpoint with default base currency (USD)"""
        response = client.get('/api/rates')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check response structure
        required_fields = ['base_currency', 'rates', 'timestamp']
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from rates response"
        
        # Check default base currency
        assert data['base_currency'] == 'USD'
        
        # Check rates structure
        assert isinstance(data['rates'], dict)
        for currency in app_config.SUPPORTED_CURRENCIES:
            assert currency in data['rates']
            assert isinstance(data['rates'][currency], (int, float))
            assert data['rates'][currency] > 0
    
    def test_rates_endpoint_specific_base_currency(self, client, app_config):
        """Test rates endpoint with specific base currency"""
        for base_currency in app_config.SUPPORTED_CURRENCIES:
            response = client.get(f'/api/rates?base={base_currency}')
            
            assert response.status_code == 200, f"Failed for base currency {base_currency}"
            data = response.get_json()
            
            assert data['base_currency'] == base_currency
            assert isinstance(data['rates'], dict)
            
            # Base currency should have rate of 1.0 to itself
            assert data['rates'][base_currency] == 1.0
    
    def test_rates_endpoint_case_insensitive_base(self, client):
        """Test that base currency parameter is case insensitive"""
        # Test lowercase
        response = client.get('/api/rates?base=eur')
        assert response.status_code == 200
        data = response.get_json()
        assert data['base_currency'] == 'EUR'
        
        # Test mixed case
        response = client.get('/api/rates?base=Gbp')
        assert response.status_code == 200
        data = response.get_json()
        assert data['base_currency'] == 'GBP'
    
    def test_rates_endpoint_unsupported_base_currency(self, client):
        """Test error handling for unsupported base currency"""
        response = client.get('/api/rates?base=INR')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'supported_currencies' in data
        assert 'INR' in data['error']
    
    def test_rates_endpoint_timestamp_format(self, client):
        """Test that rates response includes valid timestamp"""
        response = client.get('/api/rates')
        data = response.get_json()
        
        timestamp_str = data['timestamp']
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            assert isinstance(parsed_timestamp, datetime)
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")
    
    def test_rates_endpoint_wrong_method(self, client):
        """Test that non-GET methods return 405 Method Not Allowed"""
        # Test POST
        response = client.post('/api/rates')
        assert response.status_code == 405
        
        # Test PUT
        response = client.put('/api/rates')
        assert response.status_code == 405
        
        # Test DELETE
        response = client.delete('/api/rates')
        assert response.status_code == 405
    
    def test_rates_endpoint_rates_consistency(self, client, app_config):
        """Test that exchange rates are consistent across calls"""
        response1 = client.get('/api/rates?base=USD')
        response2 = client.get('/api/rates?base=USD')
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # Rates should be identical
        assert data1['rates'] == data2['rates']
        assert data1['base_currency'] == data2['base_currency']


@pytest.mark.unit
@pytest.mark.api
class TestInfoEndpoint:
    """Test cases for the /api/info endpoint"""
    
    def test_info_endpoint_returns_200(self, client):
        """Test that info endpoint returns 200 status code"""
        response = client.get('/api/info')
        assert response.status_code == 200
    
    def test_info_endpoint_returns_json(self, client):
        """Test that info endpoint returns valid JSON"""
        response = client.get('/api/info')
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert data is not None
    
    def test_info_endpoint_contains_required_fields(self, client):
        """Test that info response contains all required fields"""
        response = client.get('/api/info')
        data = response.get_json()
        
        required_fields = ['name', 'version', 'endpoints', 'supported_currencies']
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from info response"
    
    def test_info_endpoint_name_and_version(self, client, app_config):
        """Test that info endpoint returns correct name and version"""
        response = client.get('/api/info')
        data = response.get_json()
        
        assert isinstance(data['name'], str)
        assert len(data['name']) > 0
        assert 'currency converter' in data['name'].lower()
        
        assert data['version'] == app_config.API_VERSION
    
    def test_info_endpoint_endpoints_structure(self, client):
        """Test that endpoints field contains expected endpoint information"""
        response = client.get('/api/info')
        data = response.get_json()
        
        endpoints = data['endpoints']
        assert isinstance(endpoints, dict)
        
        # Check for expected endpoints
        expected_endpoints = ['health', 'convert', 'rates']
        for endpoint in expected_endpoints:
            assert endpoint in endpoints, f"Expected endpoint '{endpoint}' not found in info"
            assert isinstance(endpoints[endpoint], str)
            assert len(endpoints[endpoint]) > 0
    
    def test_info_endpoint_supported_currencies(self, client, app_config):
        """Test that info endpoint returns correct supported currencies"""
        response = client.get('/api/info')
        data = response.get_json()
        
        assert data['supported_currencies'] == app_config.SUPPORTED_CURRENCIES
        assert isinstance(data['supported_currencies'], list)
        assert len(data['supported_currencies']) > 0
    
    def test_info_endpoint_wrong_method(self, client):
        """Test that non-GET methods return 405 Method Not Allowed"""
        # Test POST
        response = client.post('/api/info')
        assert response.status_code == 405
        
        # Test PUT
        response = client.put('/api/info')
        assert response.status_code == 405
        
        # Test DELETE
        response = client.delete('/api/info')
        assert response.status_code == 405
    
    def test_info_endpoint_consistent_responses(self, client):
        """Test that multiple calls to info endpoint return consistent data"""
        response1 = client.get('/api/info')
        response2 = client.get('/api/info')
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # All fields should be identical
        assert data1 == data2


@pytest.mark.unit
@pytest.mark.api
class TestErrorHandling:
    """Test cases for API error handling"""
    
    def test_404_error_handling_api_endpoints(self, client):
        """Test 404 error handling for non-existent API endpoints"""
        response = client.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'message' in data
    
    def test_404_error_handling_health_endpoints(self, client):
        """Test 404 error handling for non-existent health endpoints"""
        response = client.get('/health/nonexistent')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_method_not_allowed_error_format(self, client):
        """Test that 405 errors return proper JSON format"""
        response = client.post('/health')
        
        assert response.status_code == 405
        data = response.get_json()
        assert 'error' in data
        assert 'message' in data
        assert 'method not allowed' in data['error'].lower()
    
    def test_json_content_type_for_errors(self, client):
        """Test that API errors return JSON content type"""
        # Test 404 error
        response = client.get('/api/nonexistent')
        assert response.content_type == 'application/json'
        
        # Test 405 error
        response = client.post('/health')
        assert response.content_type == 'application/json'


@pytest.mark.unit
@pytest.mark.api
class TestCrossEndpointConsistency:
    """Test consistency across different API endpoints"""
    
    def test_supported_currencies_consistency(self, client):
        """Test that supported currencies are consistent across all endpoints"""
        # Get supported currencies from different endpoints
        health_response = client.get('/health')
        info_response = client.get('/api/info')
        
        health_data = health_response.get_json()
        info_data = info_response.get_json()
        
        # Should be identical
        assert health_data['supported_currencies'] == info_data['supported_currencies']
    
    def test_version_consistency(self, client):
        """Test that API version is consistent across endpoints"""
        health_response = client.get('/health')
        info_response = client.get('/api/info')
        
        health_data = health_response.get_json()
        info_data = info_response.get_json()
        
        assert health_data['version'] == info_data['version']
    
    def test_exchange_rates_consistency(self, client, app_config):
        """Test that exchange rates used in conversion match rates endpoint"""
        # Get rates from rates endpoint
        rates_response = client.get('/api/rates?base=USD')
        rates_data = rates_response.get_json()
        
        # Test conversion using the same rates
        conversion_data = {'amount': 100, 'from': 'USD', 'to': 'EUR'}
        convert_response = client.post('/api/convert',
                                     data=json.dumps(conversion_data),
                                     content_type='application/json')
        convert_data = convert_response.get_json()
        
        # Exchange rate should match
        expected_rate = rates_data['rates']['EUR']
        actual_rate = convert_data['exchange_rate']
        
        assert expected_rate == actual_rate