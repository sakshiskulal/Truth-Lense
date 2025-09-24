#!/usr/bin/env python3
"""
Smoke test script for TruthLens API
Tests basic functionality without requiring actual file uploads
"""

import requests
import json
import sys
import time

API_BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on port 8000")
        return False

def test_signup():
    """Test user signup"""
    try:
        data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{API_BASE_URL}/auth/signup", data=data)
        if response.status_code == 200:
            print("✅ User signup successful")
            return response.json()["access_token"]
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return None

def test_login():
    """Test user login"""
    try:
        data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{API_BASE_URL}/auth/login", data=data)
        if response.status_code == 200:
            print("✅ User login successful")
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_profile(token):
    """Test getting user profile"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ Profile retrieval successful")
            return True
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Profile error: {e}")
        return False

def test_history(token):
    """Test getting user history"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/history", headers=headers)
        if response.status_code == 200:
            print("✅ History retrieval successful")
            return True
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History error: {e}")
        return False

def main():
    print("🚀 Starting TruthLens API smoke test...")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        sys.exit(1)
    
    # Test signup
    token = test_signup()
    if not token:
        print("⚠️  Signup failed, trying login...")
        token = test_login()
        if not token:
            print("❌ Both signup and login failed")
            sys.exit(1)
    
    # Test authenticated endpoints
    if not test_profile(token):
        sys.exit(1)
    
    if not test_history(token):
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 All tests passed! TruthLens API is working correctly.")
    print("\nNext steps:")
    print("1. Start the frontend: cd frontend && npm run dev")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Test file upload functionality")

if __name__ == "__main__":
    main()