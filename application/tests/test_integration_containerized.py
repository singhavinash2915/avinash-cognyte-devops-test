#!/usr/bin/env python3
"""
Integration tests for the containerized Currency Converter application
Tests the complete application stack running in Docker container
"""

import pytest
import requests
import time
import subprocess
import json
import os
from pathlib import Path


class ContainerManager:
    """Helper class to manage Docker container for testing"""
    
    def __init__(self, image_name="currency-converter", container_name="currency-converter-test", port=8080):
        self.image_name = image_name
        self.container_name = container_name
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.container_id = None
    
    def build_image(self):
        """Build the Docker image"""
        project_root = Path(__file__).parent.parent.parent
        print(f"Building Docker image from {project_root}")
        
        result = subprocess.run([
            "docker", "build", "-t", self.image_name, str(project_root)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Docker build failed: {result.stderr}")
            return False
        
        print("Docker image built successfully")
        return True
    
    def start_container(self):
        """Start the Docker container"""
        # Stop and remove existing container if it exists
        self.stop_container()
        
        result = subprocess.run([
            "docker", "run", "-d", 
            "-p", f"{self.port}:8080",
            "--name", self.container_name,
            self.image_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to start container: {result.stderr}")
            return False
        
        self.container_id = result.stdout.strip()
        print(f"Container started with ID: {self.container_id}")
        
        # Wait for container to be ready
        return self.wait_for_health()
    
    def wait_for_health(self, timeout=30, interval=2):
        """Wait for the container to be healthy"""
        print("Waiting for container to be ready...")
        
        for attempt in range(timeout // interval):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("Container is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(interval)
            print(f"Attempt {attempt + 1}/{timeout // interval}: Container not ready yet...")
        
        print("Container failed to become ready within timeout")
        return False
    
    def stop_container(self):
        """Stop and remove the Docker container"""
        # Stop container
        subprocess.run(["docker", "stop", self.container_name], 
                      capture_output=True, text=True)
        
        # Remove container
        subprocess.run(["docker", "rm", self.container_name], 
                      capture_output=True, text=True)
        
        self.container_id = None
    
    def get_logs(self):
        """Get container logs"""
        if self.container_id:
            result = subprocess.run(["docker", "logs", self.container_name], 
                                  capture_output=True, text=True)
            return result.stdout
        return ""


@pytest.fixture(scope="session")
def container_manager():
    """Session-scoped fixture to manage the test container"""
    manager = ContainerManager()
    
    # Build and start container
    if not manager.build_image():
        pytest.skip("Failed to build Docker image")
    
    if not manager.start_container():
        pytest.skip("Failed to start Docker container")
    
    yield manager
    
    # Cleanup
    manager.stop_container()


@pytest.fixture
def api_client(container_manager):
    """Fixture providing an API client for the containerized app"""
    return APIClient(container_manager.base_url)


class APIClient:
    """Helper class for making API requests to the containerized app"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def get(self, path):
        """Make GET request"""
        return self.session.get(f"{self.base_url}{path}")
    
    def post(self, path, data=None):
        """Make POST request"""
        return self.session.post(f"{self.base_url}{path}", json=data)


@pytest.mark.integration
@pytest.mark.slow
class TestContainerizedApp:
    """Integration tests for the containerized application"""
    
    def test_container_health_check(self, api_client):
        """Test that the health endpoint is accessible in the container"""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "supported_currencies" in data
        assert isinstance(data["supported_currencies"], list)
        assert len(data["supported_currencies"]) > 0
    
    def test_container_frontend_accessible(self, api_client):
        """Test that the frontend is accessible in the container"""
        response = api_client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Check for key elements in the HTML
        html_content = response.text
        assert "Currency Converter" in html_content
        assert "amount" in html_content.lower()
        assert "convert" in html_content.lower()
    
    def test_container_api_info(self, api_client):
        """Test the API info endpoint in the container"""
        response = api_client.get("/api/info")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["name", "version", "endpoints", "supported_currencies"]
        for field in required_fields:
            assert field in data
        
        assert "Currency Converter" in data["name"]
        assert isinstance(data["endpoints"], dict)
    
    def test_container_currency_conversion(self, api_client):
        """Test currency conversion functionality in the container"""
        conversion_data = {
            "amount": 100,
            "from": "USD",
            "to": "EUR"
        }
        
        response = api_client.post("/api/convert", conversion_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["original_amount"] == 100
        assert data["from_currency"] == "USD"
        assert data["to_currency"] == "EUR"
        assert "converted_amount" in data
        assert "exchange_rate" in data
        assert data["converted_amount"] > 0
        assert data["exchange_rate"] > 0
    
    def test_container_exchange_rates(self, api_client):
        """Test exchange rates endpoint in the container"""
        response = api_client.get("/api/rates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "base_currency" in data
        assert "rates" in data
        assert "timestamp" in data
        
        # Check that rates are provided for all supported currencies
        rates = data["rates"]
        assert isinstance(rates, dict)
        assert len(rates) > 0
        
        # All rates should be positive numbers
        for currency, rate in rates.items():
            assert isinstance(rate, (int, float))
            assert rate > 0
    
    def test_container_error_handling(self, api_client):
        """Test error handling in the containerized app"""
        # Test invalid conversion
        invalid_data = {
            "amount": "invalid",
            "from": "USD",
            "to": "EUR"
        }
        
        response = api_client.post("/api/convert", invalid_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    def test_container_unsupported_currency(self, api_client):
        """Test unsupported currency handling in the container"""
        invalid_data = {
            "amount": 100,
            "from": "USD",
            "to": "INR"  # Not supported
        }
        
        response = api_client.post("/api/convert", invalid_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "supported_currencies" in data
    
    def test_container_cors_headers(self, api_client):
        """Test that CORS headers are properly set in the container"""
        response = api_client.get("/health")
        
        # Check for CORS headers (Flask-CORS should add these)
        headers = response.headers
        assert "Access-Control-Allow-Origin" in headers or response.status_code == 200
    
    def test_container_multiple_conversions(self, api_client):
        """Test multiple currency conversions to ensure consistency"""
        test_cases = [
            {"amount": 100, "from": "USD", "to": "EUR"},
            {"amount": 50, "from": "EUR", "to": "GBP"},
            {"amount": 1000, "from": "JPY", "to": "USD"},
            {"amount": 25.5, "from": "GBP", "to": "JPY"}
        ]
        
        for test_case in test_cases:
            response = api_client.post("/api/convert", test_case)
            
            assert response.status_code == 200, f"Failed for conversion: {test_case}"
            data = response.json()
            
            assert data["success"] is True
            assert data["original_amount"] == test_case["amount"]
            assert data["from_currency"] == test_case["from"]
            assert data["to_currency"] == test_case["to"]
    
    def test_container_static_assets(self, api_client):
        """Test that static assets are served correctly"""
        # Test CSS
        response = api_client.get("/assets/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        
        # Test JavaScript files
        js_files = ["/assets/js/config.js", "/assets/js/api.js", "/assets/js/app.js"]
        for js_file in js_files:
            response = api_client.get(js_file)
            assert response.status_code == 200, f"Failed to load {js_file}"
    
    def test_container_performance(self, api_client):
        """Test basic performance of the containerized app"""
        import time
        
        # Test response time for health check
        start_time = time.time()
        response = api_client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should respond within 1 second (generous for container startup)
        assert response_time < 1.0, f"Health check took too long: {response_time:.2f}s"
        
        # Test conversion performance
        conversion_data = {"amount": 100, "from": "USD", "to": "EUR"}
        
        start_time = time.time()
        response = api_client.post("/api/convert", conversion_data)
        end_time = time.time()
        
        assert response.status_code == 200
        conversion_time = end_time - start_time
        
        # Conversion should be fast
        assert conversion_time < 1.0, f"Conversion took too long: {conversion_time:.2f}s"


@pytest.mark.integration
@pytest.mark.slow
class TestContainerizedAppEdgeCases:
    """Edge case tests for the containerized application"""
    
    def test_container_concurrent_requests(self, api_client):
        """Test handling of concurrent requests to the containerized app"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = api_client.get("/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create and start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        while not results.empty():
            result = results.get()
            assert result == 200, f"Concurrent request failed: {result}"
    
    def test_container_large_conversion_amount(self, api_client):
        """Test conversion with very large amounts"""
        large_amount_data = {
            "amount": 999999999.99,
            "from": "USD",
            "to": "EUR"
        }
        
        response = api_client.post("/api/convert", large_amount_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["converted_amount"] > 0
    
    def test_container_zero_amount_conversion(self, api_client):
        """Test conversion with zero amount"""
        zero_amount_data = {
            "amount": 0,
            "from": "USD",
            "to": "EUR"
        }
        
        response = api_client.post("/api/convert", zero_amount_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["converted_amount"] == 0
        assert data["original_amount"] == 0
    
    def test_container_logging_verification(self, container_manager):
        """Test that the container is logging properly"""
        # Make a few requests to generate logs
        api_client = APIClient(container_manager.base_url)
        api_client.get("/health")
        api_client.post("/api/convert", {"amount": 100, "from": "USD", "to": "EUR"})
        
        # Get logs
        logs = container_manager.get_logs()
        
        # Check that logs contain expected entries
        assert "Starting Currency Converter API" in logs
        assert "INFO" in logs
        assert "GET /health" in logs or "POST /api/convert" in logs