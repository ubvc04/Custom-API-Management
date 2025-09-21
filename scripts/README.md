# Scripts Directory

This directory contains utility scripts for the API Manager application.

## Available Scripts

### 🗃️ Database Management

#### `db_cleanup.py`
Comprehensive database cleanup and management utilities.

**Usage:**
```bash
python scripts/db_cleanup.py [options]
```

**Options:**
- `--clean-users` - Remove all users and related data
- `--clean-keys` - Remove all API keys and usage logs
- `--clean-logs` - Remove all usage and login logs
- `--reset-all` - Complete database reset
- `--backup` - Create backup before cleanup
- `--confirm` - Skip confirmation prompts
- `--create-admin` - Create default admin user
- `--stats` - Show database statistics

**Examples:**
```bash
# Show current database statistics
python scripts/db_cleanup.py --stats

# Clean all users with backup
python scripts/db_cleanup.py --clean-users --backup

# Complete reset with confirmation skip
python scripts/db_cleanup.py --reset-all --confirm

# Create default admin user
python scripts/db_cleanup.py --create-admin
```

**Default Admin Credentials (created with --create-admin):**
- Username: `admin`
- Email: `admin@apimanager.com`
- Password: `Admin123!`

⚠️ **Warning:** Change the default password after first login!

### 📧 OTP Testing

#### `test_otp.py`
Test suite for OTP email verification functionality.

**Usage:**
```bash
python scripts/test_otp.py
```

**Features:**
- Tests OTP generation
- Validates email templates
- Checks User model OTP methods
- Verifies SMTP configuration
- Manual email sending test

**Example Output:**
```
🧪 OTP Verification Test Suite
========================================
🔧 Testing OTP Generation...
   ✅ OTP generation working correctly

📧 Testing OTP Email Template...
   ✅ Email template function available

👤 Testing User OTP Methods...
   ✅ User OTP methods working correctly

📮 Testing SMTP Configuration...
   ✅ SMTP configuration complete

📊 Test Results Summary
==============================
✅ PASS OTP Generation
✅ PASS Email Template
✅ PASS User OTP Methods
✅ PASS SMTP Configuration

Tests passed: 4/4
🎉 All tests passed! OTP verification is working correctly.
```

## Quick Start Examples

### Reset Database and Create Admin User
```bash
# Backup current database, reset everything, and create admin
python scripts/db_cleanup.py --backup --reset-all --confirm --create-admin
```

### Test Email Functionality
```bash
# Run OTP tests to verify email is working
python scripts/test_otp.py
```

### Clean User Data Only
```bash
# Remove all users but keep database structure
python scripts/db_cleanup.py --clean-users --backup
```

### Development Workflow
```bash
# 1. Reset database for clean state
python scripts/db_cleanup.py --reset-all --confirm

# 2. Start application (creates fresh database)
python app.py

# 3. Create admin user if needed
python scripts/db_cleanup.py --create-admin

# 4. Test OTP functionality
python scripts/test_otp.py
```

## Script Permissions

### Windows
```powershell
# Make scripts executable (if needed)
powershell -ExecutionPolicy Bypass -File scripts/script_name.py
```

### Linux/Mac
```bash
# Make scripts executable
chmod +x scripts/*.py

# Run directly
./scripts/db_cleanup.py --stats
./scripts/test_otp.py
```

## Security Notes

- 🔒 **Database scripts** create backups by default
- 🔑 **Default admin** should have password changed immediately
- 📧 **Email tests** use real SMTP settings - be careful in production
- 🗃️ **Cleanup operations** are irreversible (except with backups)

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the project root directory
cd /path/to/API
python scripts/script_name.py
```

**Database Locked:**
```bash
# Stop the Flask application first
# Then run database scripts
```

**SMTP Authentication Failed:**
```bash
# Check your .env file for correct credentials
# For Gmail, use App Passwords, not regular password
```

**Permission Denied:**
```bash
# On Windows, run PowerShell as Administrator
# On Linux/Mac, check file permissions
```

### Getting Help

If you encounter issues with any scripts:

1. Check the application logs
2. Verify environment variables in `.env`
3. Ensure the Flask application is not running during database operations
4. Check file permissions and paths

For more help, see the main README.md or open an issue on GitHub.