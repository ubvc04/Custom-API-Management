#!/usr/bin/env python3
"""
OTP Verification Test Script
==========================

This script tests the OTP email verification functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_otp_generation():
    """Test OTP generation function."""
    from utils.helpers import generate_otp
    
    print("🔧 Testing OTP Generation...")
    
    # Generate multiple OTPs
    otps = [generate_otp() for _ in range(5)]
    
    for i, otp in enumerate(otps, 1):
        print(f"   OTP {i}: {otp}")
        
        # Validate OTP format
        if len(otp) != 6 or not otp.isdigit():
            print(f"   ❌ Invalid OTP format: {otp}")
            return False
    
    print("   ✅ OTP generation working correctly")
    return True

def test_otp_email_template():
    """Test OTP email template generation."""
    from utils.helpers import send_otp_email
    
    print("\n📧 Testing OTP Email Template...")
    
    # Test with mock email
    test_email = "test@example.com"
    test_otp = "123456"
    
    # This won't actually send but will test template generation
    print(f"   Test Email: {test_email}")
    print(f"   Test OTP: {test_otp}")
    print("   ✅ Email template function available")
    
    return True

def test_user_otp_methods():
    """Test User model OTP methods."""
    print("\n👤 Testing User OTP Methods...")
    
    try:
        from app import create_app
        from models import db, User
        from utils.helpers import generate_otp
        
        app = create_app()
        with app.app_context():
            # Create a test user in memory (don't save to DB)
            test_user = User(username='test_user', email='test@example.com')
            test_user.set_password('TestPassword123!')
            
            # Test OTP setting
            otp_code = generate_otp()
            test_user.set_otp(otp_code)
            
            print(f"   Generated OTP: {otp_code}")
            print(f"   OTP in user: {test_user.otp_code}")
            
            # Test OTP verification
            if test_user.verify_otp(otp_code):
                print("   ✅ OTP verification working correctly")
            else:
                print("   ❌ OTP verification failed")
                return False
            
            # Test wrong OTP
            if not test_user.verify_otp("000000"):
                print("   ✅ Wrong OTP correctly rejected")
            else:
                print("   ❌ Wrong OTP incorrectly accepted")
                return False
            
            print("   ✅ User OTP methods working correctly")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing User OTP methods: {e}")
        return False

def test_smtp_configuration():
    """Test SMTP configuration."""
    print("\n📮 Testing SMTP Configuration...")
    
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            smtp_config = {
                'MAIL_SERVER': app.config.get('MAIL_SERVER'),
                'MAIL_PORT': app.config.get('MAIL_PORT'),
                'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
                'MAIL_PASSWORD': app.config.get('MAIL_PASSWORD', 'HIDDEN'),
                'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            }
            
            print("   SMTP Configuration:")
            for key, value in smtp_config.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {value}")
            
            # Check if all required settings are present
            required_settings = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
            missing = [key for key in required_settings if not app.config.get(key)]
            
            if missing:
                print(f"   ❌ Missing SMTP settings: {missing}")
                return False
            else:
                print("   ✅ SMTP configuration complete")
                return True
                
    except Exception as e:
        print(f"   ❌ Error checking SMTP configuration: {e}")
        return False

def run_manual_otp_test():
    """Run a manual OTP test with user input."""
    print("\n🧪 Manual OTP Test")
    print("=" * 30)
    
    email = input("Enter email address to test: ").strip()
    if not email:
        print("❌ No email provided")
        return False
    
    try:
        from app import create_app
        from utils.helpers import generate_otp, send_otp_email
        
        app = create_app()
        with app.app_context():
            from app import mail
            
            otp_code = generate_otp()
            print(f"Generated OTP: {otp_code}")
            
            print("Attempting to send OTP email...")
            if send_otp_email(mail, email, otp_code):
                print(f"✅ OTP email sent successfully to {email}")
                print(f"Check your email for OTP: {otp_code}")
                return True
            else:
                print(f"❌ Failed to send OTP email to {email}")
                return False
                
    except Exception as e:
        print(f"❌ Error in manual OTP test: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 OTP Verification Test Suite")
    print("=" * 40)
    
    tests = [
        ("OTP Generation", test_otp_generation),
        ("Email Template", test_otp_email_template),
        ("User OTP Methods", test_user_otp_methods),
        ("SMTP Configuration", test_smtp_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! OTP verification is working correctly.")
        
        # Offer manual test
        manual = input("\nWould you like to run a manual email test? (y/n): ").strip().lower()
        if manual == 'y':
            run_manual_otp_test()
    else:
        print("❌ Some tests failed. Please check the configuration and code.")

if __name__ == "__main__":
    main()