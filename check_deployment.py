#!/usr/bin/env python3
"""
Quick deployment verification script.
"""
import os
import sys

def check_environment():
    print("🔍 Checking deployment environment...")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check environment variables
    important_vars = [
        'DJANGO_SETTINGS_MODULE',
        'RAILWAY_ENVIRONMENT', 
        'DATABASE_URL',
        'SECRET_KEY',
        'PORT'
    ]
    
    print("\n📋 Environment Variables:")
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        if var == 'SECRET_KEY' and value != 'NOT SET':
            value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***HIDDEN***"
        print(f"  {var}: {value}")
    
    # Try importing Django
    try:
        import django
        print(f"\n✅ Django version: {django.get_version()}")
    except ImportError:
        print("\n❌ Django not found!")
        return False
    
    # Try importing settings
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.production')
        from django.conf import settings
        print(f"✅ Settings loaded: {settings.SETTINGS_MODULE}")
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if check_environment():
        print("\n🎉 Environment looks good!")
        sys.exit(0)
    else:
        print("\n💥 Environment check failed!")
        sys.exit(1)