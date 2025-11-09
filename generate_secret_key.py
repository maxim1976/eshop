#!/usr/bin/env python3
"""
Generate a new Django secret key for production deployment.
Run this script and use the generated key in your Railway environment variables.
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    print("🔐 New Django Secret Key for Production:")
    print("=" * 60)
    print(get_random_secret_key())
    print("=" * 60)
    print("\n📝 Instructions:")
    print("1. Copy the secret key above")
    print("2. Go to your Railway project dashboard")
    print("3. Set SECRET_KEY environment variable to this value")
    print("4. Never commit this key to version control!")