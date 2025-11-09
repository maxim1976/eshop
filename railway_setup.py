#!/usr/bin/env python3
"""
Railway database setup script.
Run this in Railway terminal to populate the production database.
"""
import os
import django
from pathlib import Path

# Configure Django settings for Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.production')
django.setup()

def check_railway_database():
    """Check if we're in Railway environment and database is accessible"""
    print("🔍 Checking Railway database connection...")
    
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Ensure all migrations are applied"""
    print("🔧 Applying database migrations...")
    from django.core.management import execute_from_command_line
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main setup function for Railway"""
    print("🚀 Setting up Railway database...")
    
    # Check environment
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    if railway_env:
        print(f"📡 Railway environment detected: {railway_env}")
    else:
        print("⚠️  Not in Railway environment, continuing anyway...")
    
    # Check database connection
    if not check_railway_database():
        return False
    
    # Run migrations
    if not run_migrations():
        return False
    
    # Now import and run the main population script
    print("📦 Importing population script...")
    try:
        # Import the main populate function from populate_database.py
        import sys
        sys.path.append('.')
        from populate_database import main as populate_main
        populate_main()
        return True
    except Exception as e:
        print(f"❌ Population failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 Railway database setup completed successfully!")
        print("📝 Next steps:")
        print("   1. Visit your Railway app URL")
        print("   2. Go to /admin/ to access admin panel")
        print("   3. Login with: admin@eshop.com / admin123456")
    else:
        print("\n💥 Railway database setup failed!")
        print("Check Railway logs for more details.")