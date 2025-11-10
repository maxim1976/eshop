#!/usr/bin/env python
"""
Helper script to migrate data to PostgreSQL for Railway deployment.
Run this after setting up PostgreSQL environment variables.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.production')

# Setup Django
django.setup()

def migrate_to_postgres():
    """Migrate existing data to PostgreSQL."""
    print("Starting migration to PostgreSQL...")
    
    # First, run migrations
    from django.core.management import execute_from_command_line
    print("Running migrations...")
    execute_from_command_line(['migrate_postgres.py', 'migrate'])
    
    # Create superuser if needed
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        from django.core.management import call_command
        call_command('createsuperuser', '--noinput', 
                    '--email', 'admin@ririshenmeat.com',
                    '--first_name', 'Admin')
        
        # Set password for superuser
        admin = User.objects.get(email='admin@ririshenmeat.com')
        admin.set_password('admin123')
        admin.save()
        print("Superuser created: admin@ririshenmeat.com / admin123")
    
    # Create sample categories if they don't exist
    from products.models import Category
    if not Category.objects.exists():
        print("Creating sample categories...")
        categories = [
            {'name': '牛肉', 'name_en': 'Beef', 'slug': 'beef'},
            {'name': '豬肉', 'name_en': 'Pork', 'slug': 'pork'},
            {'name': '雞肉', 'name_en': 'Chicken', 'slug': 'chicken'},
            {'name': '羊肉', 'name_en': 'Lamb', 'slug': 'lamb'},
            {'name': '海鮮', 'name_en': 'Seafood', 'slug': 'seafood'},
            {'name': '加工品', 'name_en': 'Processed', 'slug': 'processed'},
        ]
        for cat_data in categories:
            Category.objects.create(**cat_data)
        print("Categories created")
    
    print("Migration completed successfully!")
    print("Next steps:")
    print("1. Set environment variables on Railway:")
    print("   - DATABASE_URL=postgresql://postgres:GTXmeZStEhDuOPTsqlljirnfwXwSuWIA@postgres.railway.internal:5432/railway")
    print("   - DJANGO_SETTINGS_MODULE=eshop.settings.production")
    print("   - DEBUG=False")
    print("   - ALLOWED_HOSTS=*.railway.app,localhost")
    print("2. Deploy to Railway")
    print("3. Run 'python manage.py collectstatic' if needed")

if __name__ == '__main__':
    migrate_to_postgres()