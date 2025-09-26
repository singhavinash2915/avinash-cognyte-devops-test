#!/usr/bin/env python3
"""
Integration test for the separate backend and frontend services
"""

import requests
import json

def test_integration():
    """Test the complete integration"""
    print("🧪 Testing Backend-Frontend Integration")
    print("=" * 50)
    
    # Test backend health
    print("\n1. Testing Backend API Health...")
    try:
        response = requests.get('http://127.0.0.1:5004/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Supported currencies: {', '.join(data['supported_currencies'])}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False
    
    # Test frontend serving
    print("\n2. Testing Frontend Server...")
    try:
        response = requests.get('http://127.0.0.1:8082/')
        if response.status_code == 200 and 'Currency Converter' in response.text:
            print("✅ Frontend serving HTML correctly")
        else:
            print(f"❌ Frontend HTML test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
    
    # Test frontend assets
    print("\n3. Testing Frontend Assets...")
    try:
        # Test CSS
        css_response = requests.get('http://127.0.0.1:8082/assets/css/style.css')
        if css_response.status_code == 200:
            print("✅ CSS file loaded successfully")
        
        # Test JS config
        js_response = requests.get('http://127.0.0.1:8082/assets/js/config.js')
        if js_response.status_code == 200 and '5004' in js_response.text:
            print("✅ JavaScript config loaded with correct API URL")
        
    except Exception as e:
        print(f"❌ Asset loading error: {e}")
    
    # Test API conversion
    print("\n4. Testing Currency Conversion API...")
    try:
        conversion_data = {
            "amount": 100,
            "from": "USD",
            "to": "EUR"
        }
        response = requests.post(
            'http://127.0.0.1:5004/api/convert',
            json=conversion_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Conversion successful:")
                print(f"   {data['original_amount']} {data['from_currency']} = {data['converted_amount']} {data['to_currency']}")
                print(f"   Exchange rate: {data['exchange_rate']}")
            else:
                print(f"❌ Conversion failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Conversion API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Conversion test error: {e}")
    
    # Test CORS (simulate frontend request)
    print("\n5. Testing CORS Configuration...")
    try:
        headers = {
            'Origin': 'http://127.0.0.1:8082',
            'Content-Type': 'application/json'
        }
        response = requests.options('http://127.0.0.1:5004/api/convert', headers=headers)
        if response.status_code == 200:
            print("✅ CORS preflight request successful")
        else:
            print(f"⚠️  CORS preflight returned: {response.status_code}")
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Integration test completed!")
    print(f"📱 Frontend URL: http://127.0.0.1:8082")
    print(f"🔧 Backend API: http://127.0.0.1:5004")
    print("=" * 50)

if __name__ == '__main__':
    test_integration()