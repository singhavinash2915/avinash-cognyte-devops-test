#!/usr/bin/env python3
"""
Unit tests for the /health endpoint
"""

import pytest
import json
from datetime import datetime


@pytest.mark.unit
@pytest.mark.api
class TestHealthEndpoint:
    """Test cases for the health check endpoint"""
    
    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200 status code"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_endpoint_returns_json(self, client):
        """Test that health endpoint returns valid JSON"""
        response = client.get('/health')
        assert response.content_type == 'application/json'
        
        # Should be able to parse as JSON
        data = response.get_json()
        assert data is not None
    
    def test_health_endpoint_contains_required_fields(self, client, app_config):
        """Test that health response contains all required fields"""
        response = client.get('/health')
        data = response.get_json()
        
        # Check required fields exist
        required_fields = ['status', 'message', 'version', 'timestamp', 'supported_currencies']
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from health response"
    
    def test_health_endpoint_status_is_healthy(self, client):
        """Test that health endpoint reports healthy status"""
        response = client.get('/health')
        data = response.get_json()
        
        assert data['status'] == 'healthy'
    
    def test_health_endpoint_version_matches_config(self, client, app_config):
        """Test that health endpoint returns correct API version"""
        response = client.get('/health')
        data = response.get_json()
        
        assert data['version'] == app_config.API_VERSION
    
    def test_health_endpoint_supported_currencies(self, client, app_config):
        """Test that health endpoint returns correct supported currencies"""
        response = client.get('/health')
        data = response.get_json()
        
        assert data['supported_currencies'] == app_config.SUPPORTED_CURRENCIES
        assert isinstance(data['supported_currencies'], list)
        assert len(data['supported_currencies']) > 0
    
    def test_health_endpoint_timestamp_format(self, client):
        """Test that health endpoint returns valid ISO timestamp"""
        response = client.get('/health')
        data = response.get_json()
        
        # Should be able to parse the timestamp
        timestamp_str = data['timestamp']
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            assert isinstance(parsed_timestamp, datetime)
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")
    
    def test_health_endpoint_message_content(self, client):
        """Test that health endpoint returns appropriate message"""
        response = client.get('/health')
        data = response.get_json()
        
        message = data['message']
        assert isinstance(message, str)
        assert len(message) > 0
        assert 'currency converter' in message.lower() or 'api' in message.lower()
    
    def test_health_endpoint_multiple_calls_consistent(self, client):
        """Test that multiple calls to health endpoint return consistent data"""
        response1 = client.get('/health')
        response2 = client.get('/health')
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # These fields should be identical across calls
        consistent_fields = ['status', 'message', 'version', 'supported_currencies']
        for field in consistent_fields:
            assert data1[field] == data2[field]
    
    def test_health_endpoint_wrong_method_not_allowed(self, client):
        """Test that non-GET methods return 405 Method Not Allowed"""
        # Test POST
        response = client.post('/health')
        assert response.status_code == 405
        
        # Test PUT  
        response = client.put('/health')
        assert response.status_code == 405
        
        # Test DELETE
        response = client.delete('/health')
        assert response.status_code == 405
    
    def test_health_endpoint_with_query_params(self, client):
        """Test that health endpoint works with query parameters (ignores them)"""
        response = client.get('/health?test=value&another=param')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'