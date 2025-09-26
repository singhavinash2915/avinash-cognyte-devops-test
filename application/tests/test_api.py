#!/usr/bin/env python3
"""
Simple test script to verify Flask API is working
"""

import requests
import json

# Test health endpoint
print("Testing /health endpoint...")
try:
    response = requests.get('http://localhost:3000/health')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test conversion endpoint
print("Testing /convert endpoint...")
try:
    data = {
        "amount": 100,
        "from": "USD",
        "to": "EUR"
    }
    response = requests.post('http://localhost:3000/convert', json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test another conversion
print("Testing /convert endpoint (GBP to JPY)...")
try:
    data = {
        "amount": 50,
        "from": "GBP", 
        "to": "JPY"
    }
    response = requests.post('http://localhost:3000/convert', json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test error case
print("Testing error case (invalid currency)...")
try:
    data = {
        "amount": 100,
        "from": "USD",
        "to": "INR"  # Not supported
    }
    response = requests.post('http://localhost:3000/convert', json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")