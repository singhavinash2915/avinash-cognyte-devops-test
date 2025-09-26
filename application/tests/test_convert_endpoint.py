#!/usr/bin/env python3
"""
Unit tests for the /api/convert endpoint
"""

import pytest
import json
from datetime import datetime


@pytest.mark.unit
@pytest.mark.api
class TestConvertEndpoint:
    """Test cases for the currency conversion endpoint"""
    
    def test_convert_endpoint_valid_conversion(self, client, sample_conversion_data):
        """Test successful currency conversion with valid data"""
        data = sample_conversion_data['valid_conversion']
        response = client.post('/api/convert', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Check response structure
        required_fields = ['success', 'original_amount', 'from_currency', 'to_currency', 
                          'converted_amount', 'exchange_rate', 'timestamp']
        for field in required_fields:
            assert field in result, f"Required field '{field}' missing from conversion response"
        
        # Check values
        assert result['success'] is True
        assert result['original_amount'] == data['amount']
        assert result['from_currency'] == data['from']
        assert result['to_currency'] == data['to']
        assert isinstance(result['converted_amount'], (int, float))
        assert isinstance(result['exchange_rate'], (int, float))
        assert result['converted_amount'] > 0
        assert result['exchange_rate'] > 0
    
    def test_convert_endpoint_same_currency(self, client, sample_conversion_data):
        """Test conversion between same currencies (should return same amount)"""
        data = sample_conversion_data['same_currency']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        
        assert result['success'] is True
        assert result['original_amount'] == result['converted_amount']
        assert result['exchange_rate'] == 1.0
        assert result['from_currency'] == result['to_currency']
    
    def test_convert_endpoint_decimal_amount(self, client, sample_conversion_data):
        """Test conversion with decimal amounts"""
        data = sample_conversion_data['decimal_amount']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        
        assert result['success'] is True
        assert result['original_amount'] == data['amount']
        # Converted amount should be rounded to 2 decimal places
        assert round(result['converted_amount'], 2) == result['converted_amount']
    
    def test_convert_endpoint_zero_amount(self, client, sample_conversion_data):
        """Test conversion with zero amount"""
        data = sample_conversion_data['zero_amount']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        
        assert result['success'] is True
        assert result['original_amount'] == 0.0
        assert result['converted_amount'] == 0.0
    
    def test_convert_endpoint_calculation_accuracy(self, client, app_config):
        """Test that conversion calculations are accurate"""
        # Test known conversion: 100 USD to EUR
        data = {'amount': 100, 'from': 'USD', 'to': 'EUR'}
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        result = response.get_json()
        expected_rate = app_config.EXCHANGE_RATES['USD']['EUR']
        expected_amount = round(100 * expected_rate, 2)
        
        assert result['exchange_rate'] == expected_rate
        assert result['converted_amount'] == expected_amount
    
    def test_convert_endpoint_timestamp_format(self, client, sample_conversion_data):
        """Test that conversion response includes valid timestamp"""
        data = sample_conversion_data['valid_conversion']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        result = response.get_json()
        timestamp_str = result['timestamp']
        
        # Should be able to parse the timestamp
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            assert isinstance(parsed_timestamp, datetime)
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")
    
    def test_convert_endpoint_missing_amount(self, client, invalid_conversion_data):
        """Test error handling for missing amount"""
        data = invalid_conversion_data['missing_amount']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'amount' in result['error'].lower()
    
    def test_convert_endpoint_negative_amount(self, client, invalid_conversion_data):
        """Test error handling for negative amount"""
        data = invalid_conversion_data['negative_amount']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'positive' in result['error'].lower()
    
    def test_convert_endpoint_invalid_amount(self, client, invalid_conversion_data):
        """Test error handling for non-numeric amount"""
        data = invalid_conversion_data['invalid_amount']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'number' in result['error'].lower()
    
    def test_convert_endpoint_missing_currencies(self, client, invalid_conversion_data):
        """Test error handling for missing currency fields"""
        # Test missing from currency
        data = invalid_conversion_data['missing_from_currency']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test missing to currency
        data = invalid_conversion_data['missing_to_currency']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_convert_endpoint_unsupported_currencies(self, client, invalid_conversion_data):
        """Test error handling for unsupported currencies"""
        # Test unsupported from currency
        data = invalid_conversion_data['unsupported_from_currency']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'supported_currencies' in result
        
        # Test unsupported to currency
        data = invalid_conversion_data['unsupported_to_currency']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'supported_currencies' in result
    
    def test_convert_endpoint_empty_currencies(self, client, invalid_conversion_data):
        """Test error handling for empty currency strings"""
        data = invalid_conversion_data['empty_currencies']
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
    
    def test_convert_endpoint_no_json_data(self, client):
        """Test error handling when no JSON data is provided"""
        response = client.post('/api/convert')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'json' in result['error'].lower()
    
    def test_convert_endpoint_invalid_json(self, client):
        """Test error handling for malformed JSON"""
        response = client.post('/api/convert',
                             data='{"invalid": json}',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_convert_endpoint_wrong_method(self, client):
        """Test that non-POST methods return 405 Method Not Allowed"""
        # Test GET
        response = client.get('/api/convert')
        assert response.status_code == 405
        
        # Test PUT
        response = client.put('/api/convert')
        assert response.status_code == 405
        
        # Test DELETE
        response = client.delete('/api/convert')
        assert response.status_code == 405
    
    def test_convert_endpoint_case_insensitive_currencies(self, client):
        """Test that currency codes are case insensitive"""
        # Test lowercase currencies
        data = {'amount': 100, 'from': 'usd', 'to': 'eur'}
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['from_currency'] == 'USD'
        assert result['to_currency'] == 'EUR'
        
        # Test mixed case currencies
        data = {'amount': 100, 'from': 'Gbp', 'to': 'JpY'}
        response = client.post('/api/convert',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['from_currency'] == 'GBP'
        assert result['to_currency'] == 'JPY'
    
    def test_convert_endpoint_all_currency_pairs(self, client, app_config):
        """Test conversion between all supported currency pairs"""
        for from_currency in app_config.SUPPORTED_CURRENCIES:
            for to_currency in app_config.SUPPORTED_CURRENCIES:
                data = {'amount': 100, 'from': from_currency, 'to': to_currency}
                response = client.post('/api/convert',
                                     data=json.dumps(data),
                                     content_type='application/json')
                
                assert response.status_code == 200, f"Failed for {from_currency} to {to_currency}"
                result = response.get_json()
                assert result['success'] is True
                assert result['from_currency'] == from_currency
                assert result['to_currency'] == to_currency