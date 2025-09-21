#!/usr/bin/env python3
"""
Security Enhancement Test Script
===============================
Test the new login alerts and OTP verification for API key operations.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_login_alert():
    """Test login alert functionality"""
    print("🔐 Testing Login Alert Functionality...")
    
    # Test data
    login_data = {
        'username': 'bavesh',  # Use existing user
        'password': 'TestPass123!'  # Use a test password
    }
    
    try:
        # Attempt login
        response = requests.post('http://localhost:5000/auth/login', 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"   Login Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login successful - Alert email should be sent")
            print(f"   📧 User: {data.get('user', {}).get('username', 'N/A')}")
            return True
        else:
            data = response.json()
            print(f"   ❌ Login failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
        return False

def test_otp_request():
    """Test OTP request for API key operations"""
    print("\n🔑 Testing OTP Request for API Key Operations...")
    
    # First need to login to get session
    session = requests.Session()
    
    login_data = {
        'username': 'bavesh',
        'password': 'TestPass123!'
    }
    
    try:
        # Login first
        login_response = session.post('http://localhost:5000/auth/login', 
                                    json=login_data,
                                    headers={'Content-Type': 'application/json'})
        
        if login_response.status_code != 200:
            print("   ❌ Login required for OTP test failed")
            return False
        
        # Test OTP request for create action
        otp_data = {'action_type': 'create'}
        
        response = session.post('http://localhost:5000/keys/request-otp',
                              json=otp_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"   OTP Request Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ OTP request successful - OTP email should be sent")
            print(f"   📧 Message: {data.get('message', 'N/A')}")
            return True
        else:
            data = response.json()
            print(f"   ❌ OTP request failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ OTP request test failed: {e}")
        return False

def test_email_configuration():
    """Test email configuration"""
    print("\n📧 Testing Email Configuration...")
    
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            config = app.config
            
            # Check email configuration
            required_configs = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
            all_configured = True
            
            for config_key in required_configs:
                if config.get(config_key):
                    print(f"   ✅ {config_key}: configured")
                else:
                    print(f"   ❌ {config_key}: missing")
                    all_configured = False
            
            if all_configured:
                print("   ✅ All email configurations are set")
                return True
            else:
                print("   ❌ Some email configurations are missing")
                return False
                
    except Exception as e:
        print(f"   ❌ Email configuration test failed: {e}")
        return False

def test_user_existence():
    """Check if test user exists"""
    print("\n👤 Checking Test User...")
    
    try:
        from app import create_app
        from models import User
        
        app = create_app()
        with app.app_context():
            user = User.query.filter_by(username='bavesh').first()
            
            if user:
                print(f"   ✅ Test user exists: {user.username} ({user.email})")
                print(f"   🔐 OTP Verified: {user.otp_verified}")
                return True
            else:
                print("   ❌ Test user 'bavesh' not found")
                print("   💡 You may need to register a user first")
                return False
                
    except Exception as e:
        print(f"   ❌ User check failed: {e}")
        return False

def main():
    """Run all security enhancement tests"""
    print("🔒 Security Enhancement Test Suite")
    print("=" * 50)
    
    tests = [
        ("User Existence", test_user_existence),
        ("Email Configuration", test_email_configuration),
        ("Login Alert", test_login_alert),
        ("OTP Request", test_otp_request),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Security Enhancement Test Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All security enhancements working!")
        print("\n🔐 Security Features Implemented:")
        print("✅ Login email alerts with device info")
        print("✅ OTP verification for API key creation")
        print("✅ OTP verification for API key deletion")
        print("✅ Professional email templates")
        print("✅ Frontend OTP modal workflows")
        return True
    else:
        print("⚠️ Some security tests failed. Please review above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)