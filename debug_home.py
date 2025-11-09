#!/usr/bin/env python
"""
Debug script to test home view components in isolation.
This will help us identify what's causing the 500 error on Railway.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.production')
django.setup()

def test_imports():
    """Test if we can import the models successfully."""
    print("Testing imports...")
    try:
        from products.models import Product, Category
        print("✓ Successfully imported Product and Category models")
        return True
    except Exception as e:
        print(f"✗ Failed to import models: {e}")
        return False

def test_database_connection():
    """Test if we can connect to the database."""
    print("Testing database connection...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print(f"✓ Database connection successful: {result}")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_model_queries():
    """Test if we can query the models."""
    print("Testing model queries...")
    try:
        from products.models import Product, Category
        
        # Test Category query
        categories = Category.objects.filter(is_active=True).count()
        print(f"✓ Categories query successful: {categories} active categories")
        
        # Test Product query  
        products = Product.objects.filter(status='active', is_featured=True).count()
        print(f"✓ Products query successful: {products} featured products")
        
        return True
    except Exception as e:
        print(f"✗ Model queries failed: {e}")
        return False

def test_template_context():
    """Test the home view context generation."""
    print("Testing template context generation...")
    try:
        from products.models import Product, Category
        
        # Get featured products
        featured_products = Product.objects.filter(
            status='active',
            is_featured=True
        ).select_related('category').prefetch_related('images')[:6]
        
        # Get categories for display
        categories = Category.objects.filter(
            is_active=True
        ).order_by('display_order', 'name')[:6]
        
        context = {
            'featured_products': featured_products,
            'categories': categories,
        }
        
        print(f"✓ Context generated successfully:")
        print(f"  - Featured products: {len(featured_products)}")
        print(f"  - Categories: {len(categories)}")
        
        return True
    except Exception as e:
        print(f"✗ Context generation failed: {e}")
        return False

if __name__ == "__main__":
    print("Django Home View Debug Tool")
    print("=" * 40)
    
    # Test each component
    tests = [
        test_imports,
        test_database_connection,
        test_model_queries,
        test_template_context,
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            all_passed = False
        print("-" * 40)
    
    if all_passed:
        print("✓ All tests passed! The home view should work.")
    else:
        print("✗ Some tests failed. Check the errors above.")