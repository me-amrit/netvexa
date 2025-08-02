#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "company_name": "Test Company"
    }
    
    print(f"Testing registration at {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ Registration successful!")
            return response.json()
        else:
            print("✗ Registration failed!")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": email,  # OAuth2 expects 'username' field
        "password": password
    }
    
    print(f"\nTesting login at {url}")
    
    try:
        response = requests.post(url, data=data)  # Form data, not JSON
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ Login successful!")
            return response.json()
        else:
            print("✗ Login failed!")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_health():
    """Test health endpoint"""
    url = f"{BASE_URL}/"
    
    print(f"Testing health at {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== NETVEXA API Test ===\n")
    
    # Test health
    if test_health():
        print("\n✓ Backend is running!")
    else:
        print("\n✗ Backend is not accessible!")
        exit(1)
    
    # Test registration
    print("\n--- Testing Registration ---")
    result = test_registration()
    
    # If registration worked or user exists, test login
    print("\n--- Testing Login ---")
    test_login("test@example.com", "TestPassword123!")