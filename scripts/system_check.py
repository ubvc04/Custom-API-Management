#!/usr/bin/env python3
"""
API Manager System Check
========================
Comprehensive system status and health check script.
"""

import os
import sys
import random
import smtplib

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔧 Testing Module Imports...")
    
    try:
        from app import create_app
        print("   ✅ Flask app can be imported")
    except Exception as e:
        print(f"   ❌ Flask app import failed: {e}")
        return False
    
    try:
        from models import db, User, ApiKey, ApiUsage, LoginHistory
        print("   ✅ Database models can be imported")
    except Exception as e:
        print(f"   ❌ Database models import failed: {e}")
        return False
        
    try:
        from utils.helpers import generate_otp, send_otp_email
        print("   ✅ Helper functions can be imported")
    except Exception as e:
        print(f"   ❌ Helper functions import failed: {e}")
        return False
        
    return True

def test_database():
    """Test database connectivity and operations"""
    print("\n🗃️ Testing Database...")
    
    try:
        from app import create_app
        from models import db, User
        
        app = create_app()
        with app.app_context():
            # Test database connection
            users = User.query.count()
            print(f"   ✅ Database connected - {users} users found")
            
            # Test if admin exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("   ✅ Admin user exists")
            else:
                print("   ⚠️ No admin user found")
                
            return True
            
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    print("\n📧 Testing Email Configuration...")
    
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            config = app.config
            
            # Check all required email configs
            required_configs = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
            all_configured = True
            
            for config_key in required_configs:
                if config.get(config_key):
                    print(f"   ✅ {config_key}: configured")
                else:
                    print(f"   ❌ {config_key}: missing")
                    all_configured = False
                    
            return all_configured
            
    except Exception as e:
        print(f"   ❌ Email config test failed: {e}")
        return False

def test_otp_generation():
    """Test OTP generation functionality"""
    print("\n🔐 Testing OTP Generation...")
    
    try:
        from utils.helpers import generate_otp
        
        # Generate multiple OTPs to test randomness
        otps = []
        for i in range(5):
            otp = generate_otp()
            otps.append(otp)
            
        # Check if OTPs are 6 digits and different
        all_valid = True
        for otp in otps:
            if not (isinstance(otp, str) and len(otp) == 6 and otp.isdigit()):
                all_valid = False
                break
                
        if all_valid and len(set(otps)) > 1:  # At least some should be different
            print("   ✅ OTP generation working correctly")
            print(f"   📋 Sample OTPs: {', '.join(otps[:3])}")
            return True
        else:
            print("   ❌ OTP generation issues detected")
            return False
            
    except Exception as e:
        print(f"   ❌ OTP generation test failed: {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection without sending email"""
    print("\n📮 Testing SMTP Connection...")
    
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            config = app.config
            
            server = smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT'])
            server.starttls()
            server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
            server.quit()
            
            print("   ✅ SMTP connection successful")
            return True
            
    except Exception as e:
        print(f"   ❌ SMTP connection failed: {e}")
        return False

def test_routes():
    """Test that main routes are accessible"""
    print("\n🌐 Testing Application Routes...")
    
    try:
        from app import create_app
        
        app = create_app()
        client = app.test_client()
        
        # Test main routes
        routes_to_test = [
            ('/', 'Home page'),
            ('/auth/login', 'Login page'),
            ('/auth/register', 'Register page'),
        ]
        
        all_routes_ok = True
        for route, description in routes_to_test:
            response = client.get(route)
            if response.status_code == 200:
                print(f"   ✅ {description}: accessible")
            else:
                print(f"   ❌ {description}: status {response.status_code}")
                all_routes_ok = False
                
        return all_routes_ok
        
    except Exception as e:
        print(f"   ❌ Route testing failed: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔑 Checking Environment Variables...")
    
    required_env_vars = [
        'SECRET_KEY',
        'SMTP_SERVER',
        'SMTP_USERNAME',
        'SMTP_PASSWORD'
    ]
    
    all_set = True
    for var in required_env_vars:
        if os.getenv(var):
            print(f"   ✅ {var}: set")
        else:
            print(f"   ❌ {var}: missing")
            all_set = False
            
    return all_set

def main():
    """Run comprehensive system check"""
    print("🔍 API Manager System Health Check")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Variables", check_environment),
        ("Database", test_database),
        ("Email Configuration", test_email_config),
        ("OTP Generation", test_otp_generation),
        ("SMTP Connection", test_smtp_connection),
        ("Application Routes", test_routes),
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
    print("📊 System Health Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems operational!")
        print("\n🚀 Your API Manager is ready to use!")
        print("\nNext steps:")
        print("1. Start the application: python app.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Register a new account or login with admin credentials")
        return True
    else:
        print("⚠️ Some issues detected. Please review failed tests above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)