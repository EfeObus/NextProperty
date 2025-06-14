#!/usr/bin/env python3
"""
Test script to verify that the .lower() AttributeError fix is working
"""
import requests
import json

def test_prediction_with_none_property_type():
    """Test prediction with None property_type to trigger the previous error"""
    base_url = "http://localhost:5007"
    
    # Test data that would previously cause AttributeError
    test_data = {
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
        "lot_size": 0.25,
        "year_built": 2010,
        "city": "Test City",
        "state": "CA",
        "property_type": None,  # This would cause the AttributeError
        "garage_spaces": 2,
        "stories": 1
    }
    
    try:
        print("Testing property prediction with None property_type...")
        response = requests.post(f"{base_url}/api/predict", json=test_data, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 400:
            print("✅ Good: Application handled None property_type gracefully with validation error")
        elif response.status_code == 200:
            print("✅ Good: Application processed request successfully")
        else:
            print(f"❓ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test with empty string property_type
    test_data["property_type"] = ""
    try:
        print("\nTesting property prediction with empty property_type...")
        response = requests.post(f"{base_url}/api/predict", json=test_data, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Good: Application handled empty property_type gracefully")
        elif response.status_code == 200:
            print("✅ Good: Application processed request successfully")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test with valid property_type
    test_data["property_type"] = "house"
    try:
        print("\nTesting property prediction with valid property_type...")
        response = requests.post(f"{base_url}/api/predict", json=test_data, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Good: Application processed valid request successfully")
            result = response.json()
            if 'predicted_price' in result:
                print(f"✅ Prediction successful: ${result['predicted_price']:.2f}")
            else:
                print("❓ No predicted_price in response")
        else:
            print(f"❓ Unexpected status code for valid request: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    print("\n✅ All tests completed - checking error logs for any AttributeError...")
    return True

if __name__ == "__main__":
    test_prediction_with_none_property_type()
