#!/usr/bin/env python3
"""
Integration test to verify frontend and backend work together
"""

import requests
import re

# Test configuration
BASE_URL = 'http://localhost:5001'

def test_frontend_integration():
    """Test complete frontend and backend integration"""
    
    print("=== Frontend and Backend Integration Test ===\n")
    
    # Test 1: Frontend HTML is served
    print("1. Testing frontend HTML delivery...")
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code == 200 and 'Currency Converter' in response.text:
            print("✅ Frontend HTML served successfully")
        else:
            print(f"❌ Frontend HTML test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend HTML test error: {e}")
        return False
    
    # Test 2: Static CSS file is accessible
    print("\n2. Testing static CSS file...")
    try:
        css_response = requests.get(f'{BASE_URL}/static/css/style.css')
        if css_response.status_code == 200 and 'Currency Converter Styles' in css_response.text:
            print("✅ CSS file served successfully")
        else:
            print(f"❌ CSS file test failed: {css_response.status_code}")
    except Exception as e:
        print(f"❌ CSS file test error: {e}")
    
    # Test 3: Static JS file is accessible  
    print("\n3. Testing static JavaScript file...")
    try:
        js_response = requests.get(f'{BASE_URL}/static/js/app.js')
        if js_response.status_code == 200 and 'handleConversion' in js_response.text:
            print("✅ JavaScript file served successfully")
        else:
            print(f"❌ JavaScript file test failed: {js_response.status_code}")
    except Exception as e:
        print(f"❌ JavaScript file test error: {e}")
    
    # Test 4: Health endpoint accessible from frontend
    print("\n4. Testing health endpoint...")
    try:
        health_response = requests.get(f'{BASE_URL}/health')
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health endpoint working: {health_data['status']}")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 5: Conversion endpoint works
    print("\n5. Testing conversion endpoint...")
    try:
        convert_data = {"amount": 150, "from": "GBP", "to": "JPY"}
        convert_response = requests.post(f'{BASE_URL}/convert', json=convert_data)
        if convert_response.status_code == 200:
            result = convert_response.json()
            print(f"✅ Conversion successful: {result['original_amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
        else:
            print(f"❌ Conversion failed: {convert_response.status_code}")
    except Exception as e:
        print(f"❌ Conversion test error: {e}")
    
    # Test 6: Error handling works
    print("\n6. Testing error handling...")
    try:
        error_data = {"amount": 100, "from": "USD", "to": "INVALID"}
        error_response = requests.post(f'{BASE_URL}/convert', json=error_data)
        if error_response.status_code == 400:
            error_result = error_response.json()
            print(f"✅ Error handling works: {error_result['error']}")
        else:
            print(f"❌ Error handling test failed: {error_response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
    
    print("\n=== Integration Test Complete ===")
    return True

if __name__ == '__main__':
    test_frontend_integration()