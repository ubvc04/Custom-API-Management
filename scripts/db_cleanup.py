#!/usr/bin/env python3
"""
Database Cleanup Script for API Manager
========================================

This script provides utilities to clean and reset the database.
Use with caution in production environments.

Usage:
    python scripts/db_cleanup.py [options]

Options:
    --clean-users       Remove all users and related data
    --clean-keys        Remove all API keys and usage logs
    --clean-logs        Remove all usage and login logs
    --reset-all         Complete database reset
    --backup            Create backup before cleanup
    --confirm           Skip confirmation prompts
    
Examples:
    python scripts/db_cleanup.py --clean-users --backup
    python scripts/db_cleanup.py --reset-all --confirm
"""

import sys
import os
import argparse
import sqlite3
from datetime import datetime
import shutil

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Get the database file path."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'api_manager.db')

def backup_database():
    """Create a backup of the current database."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("❌ Database file not found. Nothing to backup.")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"database_backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None

def get_database_stats():
    """Get current database statistics."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['users'] = cursor.fetchone()[0]
        
        # Count API keys
        cursor.execute("SELECT COUNT(*) FROM api_keys")
        stats['api_keys'] = cursor.fetchone()[0]
        
        # Count usage logs
        cursor.execute("SELECT COUNT(*) FROM api_usage")
        stats['usage_logs'] = cursor.fetchone()[0]
        
        # Count login history
        cursor.execute("SELECT COUNT(*) FROM login_history")
        stats['login_history'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"❌ Failed to get database stats: {e}")
        return None

def clean_users(confirm=False):
    """Remove all users and their related data."""
    if not confirm:
        response = input("🚨 This will delete ALL users and their data. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return False
    
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete in correct order to respect foreign keys
        cursor.execute("DELETE FROM api_usage")
        cursor.execute("DELETE FROM api_keys")
        cursor.execute("DELETE FROM login_history")
        cursor.execute("DELETE FROM users")
        
        conn.commit()
        conn.close()
        
        print("✅ All users and related data deleted successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to clean users: {e}")
        return False

def clean_api_keys(confirm=False):
    """Remove all API keys and usage logs."""
    if not confirm:
        response = input("🚨 This will delete ALL API keys and usage logs. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return False
    
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM api_usage")
        cursor.execute("DELETE FROM api_keys")
        
        conn.commit()
        conn.close()
        
        print("✅ All API keys and usage logs deleted successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to clean API keys: {e}")
        return False

def clean_logs(confirm=False):
    """Remove all usage and login logs."""
    if not confirm:
        response = input("🚨 This will delete ALL usage and login logs. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return False
    
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM api_usage")
        cursor.execute("DELETE FROM login_history")
        
        conn.commit()
        conn.close()
        
        print("✅ All logs deleted successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to clean logs: {e}")
        return False

def reset_database(confirm=False):
    """Complete database reset - removes all data."""
    if not confirm:
        response = input("🚨 This will COMPLETELY RESET the database. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return False
    
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return False
    
    try:
        # Remove the database file
        os.remove(db_path)
        print("✅ Database reset successfully. It will be recreated on next app start.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        return False

def create_admin_user():
    """Create a default admin user."""
    print("\n🔧 Creating default admin user...")
    
    # Import here to avoid circular imports
    try:
        from app import create_app
        from models import db, User
        
        app = create_app()
        with app.app_context():
            # Check if admin already exists
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                print(f"✅ Admin user already exists: {admin.username}")
                return True
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@apimanager.com'
            )
            admin_user.set_password('Admin123!')
            admin_user.is_admin = True
            admin_user.otp_verified = True
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Default admin user created:")
            print("   Username: admin")
            print("   Email: admin@apimanager.com")
            print("   Password: Admin123!")
            print("   🚨 Please change the password after first login!")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Database cleanup utilities for API Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--clean-users', action='store_true',
                       help='Remove all users and related data')
    parser.add_argument('--clean-keys', action='store_true',
                       help='Remove all API keys and usage logs')
    parser.add_argument('--clean-logs', action='store_true',
                       help='Remove all usage and login logs')
    parser.add_argument('--reset-all', action='store_true',
                       help='Complete database reset')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup before cleanup')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompts')
    parser.add_argument('--create-admin', action='store_true',
                       help='Create default admin user')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    
    args = parser.parse_args()
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    print("🔧 API Manager Database Cleanup Tool")
    print("=" * 40)
    
    # Show current stats
    if args.stats or any([args.clean_users, args.clean_keys, args.clean_logs, args.reset_all]):
        stats = get_database_stats()
        if stats:
            print(f"\n📊 Current Database Statistics:")
            print(f"   Users: {stats['users']}")
            print(f"   API Keys: {stats['api_keys']}")
            print(f"   Usage Logs: {stats['usage_logs']}")
            print(f"   Login History: {stats['login_history']}")
        else:
            print("\n📊 Database not found or empty.")
    
    if args.stats:
        return
    
    # Create backup if requested
    if args.backup:
        print(f"\n📦 Creating backup...")
        backup_path = backup_database()
        if not backup_path:
            print("❌ Backup failed. Aborting operations.")
            return
    
    # Perform cleanup operations
    operations_performed = False
    
    if args.clean_users:
        print(f"\n🧹 Cleaning users...")
        if clean_users(args.confirm):
            operations_performed = True
    
    if args.clean_keys:
        print(f"\n🧹 Cleaning API keys...")
        if clean_api_keys(args.confirm):
            operations_performed = True
    
    if args.clean_logs:
        print(f"\n🧹 Cleaning logs...")
        if clean_logs(args.confirm):
            operations_performed = True
    
    if args.reset_all:
        print(f"\n🧹 Resetting database...")
        if reset_database(args.confirm):
            operations_performed = True
    
    if args.create_admin:
        if create_admin_user():
            operations_performed = True
    
    # Show final stats
    if operations_performed:
        print(f"\n📊 Final Database Statistics:")
        stats = get_database_stats()
        if stats:
            print(f"   Users: {stats['users']}")
            print(f"   API Keys: {stats['api_keys']}")
            print(f"   Usage Logs: {stats['usage_logs']}")
            print(f"   Login History: {stats['login_history']}")
        else:
            print("   Database is empty or will be recreated.")
        
        print(f"\n✅ Database cleanup completed successfully!")
    else:
        print(f"\n❌ No operations performed.")

if __name__ == "__main__":
    main()