#!/usr/bin/env python3
"""
Simple test to check if Flask app works
"""

# Import and test the app directly
import sys
sys.path.append('app')
from app import app

if __name__ == '__main__':
    print("Testing Flask app directly...")
    
    with app.test_client() as client:
        # Test health endpoint
        print("\n=== Testing /health endpoint ===")
        response = client.get('/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test convert endpoint
        print("\n=== Testing /convert endpoint ===")
        data = {"amount": 100, "from": "USD", "to": "EUR"}
        response = client.post('/convert', json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test another conversion
        print("\n=== Testing GBP to JPY conversion ===")
        data = {"amount": 50, "from": "GBP", "to": "JPY"}
        response = client.post('/convert', json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test error case
        print("\n=== Testing error case (invalid currency) ===")
        data = {"amount": 100, "from": "USD", "to": "INR"}
        response = client.post('/convert', json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
    print("\n=== Testing complete! ===")