#!/usr/bin/env python3
"""
Script to create initial data for the e-commerce site.
Run this after migrations to populate the database with sample data.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.development')
django.setup()

from products.models import Category, Product, ProductImage
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
import random

User = get_user_model()

def create_categories():
    """Create product categories"""
    categories = [
        {'name': '美國安格斯牛肉', 'name_en': 'American Angus Beef', 'slug': 'american-angus', 'display_order': 1},
        {'name': '台灣優質豬肉', 'name_en': 'Taiwan Premium Pork', 'slug': 'taiwan-premium', 'display_order': 2},
        {'name': '新鮮海鮮', 'name_en': 'Fresh Seafood', 'slug': 'seafood', 'display_order': 3},
        {'name': '雞肉產品', 'name_en': 'Poultry Products', 'slug': 'poultry', 'display_order': 4},
        {'name': '加工製品', 'name_en': 'Processed Foods', 'slug': 'processed', 'display_order': 5},
        {'name': '冷凍食品', 'name_en': 'Frozen Foods', 'slug': 'frozen', 'display_order': 6},
    ]
    
    created_categories = []
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'name_en': cat_data['name_en'],
                'display_order': cat_data['display_order'],
                'is_active': True,
            }
        )
        created_categories.append(category)
        print(f"{'Created' if created else 'Found'} category: {category.name}")
    
    return created_categories

def create_products(categories):
    """Create sample products"""
    products_data = [
        # American Angus Beef
        {
            'name': '美國1855頂級牛小排',
            'name_en': 'USDA 1855 Prime Beef Short Ribs',
            'slug': 'usda-1855-beef-short-ribs',
            'sku': 'BEEF-1855-SR-001',
            'category': 'american-angus',
            'description': '美國1855頂級牛小排，肉質鮮美，適合燒烤',
            'description_en': 'USDA 1855 Prime Beef Short Ribs, perfect for grilling',
            'price': 1200,
            'weight': 500,
            'is_featured': True,
        },
        {
            'name': '美國Choice級牛肋眼',
            'name_en': 'USDA Choice Ribeye Steak',
            'slug': 'usda-choice-ribeye',
            'sku': 'BEEF-CHOICE-RE-002',
            'category': 'american-angus',
            'description': '美國Choice級牛肋眼，油花豐富，口感絕佳',
            'description_en': 'USDA Choice Ribeye with excellent marbling',
            'price': 800,
            'sale_price': 720,
            'weight': 300,
            'is_featured': True,
        },
        # Taiwan Premium Pork
        {
            'name': '台灣1983神豬梅花肉',
            'name_en': 'Taiwan 1983 Premium Pork Shoulder',
            'slug': 'taiwan-1983-pork-shoulder',
            'sku': 'PORK-1983-PS-003',
            'category': 'taiwan-premium',
            'description': '台灣1983神豬梅花肉，本土優質豬肉',
            'description_en': 'Taiwan 1983 Premium Pork Shoulder, locally raised',
            'price': 350,
            'weight': 600,
            'is_featured': True,
        },
        {
            'name': '台灣黑豬五花肉',
            'name_en': 'Taiwan Black Pork Belly',
            'slug': 'taiwan-black-pork-belly',
            'sku': 'PORK-BLACK-PB-004',
            'category': 'taiwan-premium',
            'description': '台灣黑豬五花肉，肉質Q彈有勁',
            'description_en': 'Taiwan Black Pork Belly, tender and flavorful',
            'price': 280,
            'weight': 500,
        },
        # Fresh Seafood
        {
            'name': '花蓮野生石斑魚',
            'name_en': 'Hualien Wild Grouper',
            'slug': 'hualien-wild-grouper',
            'sku': 'SEAFOOD-GROUPER-005',
            'category': 'seafood',
            'description': '花蓮外海野生石斑魚，肉質鮮甜',
            'description_en': 'Wild caught grouper from Hualien waters',
            'price': 600,
            'weight': 800,
            'is_featured': True,
        },
        {
            'name': '新鮮白蝦',
            'name_en': 'Fresh White Shrimp',
            'slug': 'fresh-white-shrimp',
            'sku': 'SEAFOOD-SHRIMP-006',
            'category': 'seafood',
            'description': '新鮮白蝦，適合各種料理方式',
            'description_en': 'Fresh white shrimp, perfect for any cooking style',
            'price': 450,
            'weight': 300,
        },
        # Poultry
        {
            'name': '土雞全雞',
            'name_en': 'Free Range Whole Chicken',
            'slug': 'free-range-whole-chicken',
            'sku': 'POULTRY-CHICKEN-007',
            'category': 'poultry',
            'description': '放山土雞，肉質結實鮮美',
            'description_en': 'Free range whole chicken, firm and delicious',
            'price': 320,
            'weight': 1200,
            'is_featured': True,
        },
    ]
    
    # Get categories by slug for easy lookup
    cat_lookup = {cat.slug: cat for cat in categories}
    
    created_products = []
    for prod_data in products_data:
        category = cat_lookup.get(prod_data['category'])
        if not category:
            continue
            
        product, created = Product.objects.get_or_create(
            slug=prod_data['slug'],
            defaults={
                'name': prod_data['name'],
                'name_en': prod_data['name_en'],
                'sku': prod_data['sku'],
                'category': category,
                'description': prod_data['description'],
                'description_en': prod_data['description_en'],
                'price': prod_data['price'],
                'sale_price': prod_data.get('sale_price'),
                'weight': prod_data['weight'],
                'is_featured': prod_data.get('is_featured', False),
                'status': 'active',
                'stock': random.randint(10, 50),  # Use 'stock' not 'stock_quantity'
            }
        )
        created_products.append(product)
        print(f"{'Created' if created else 'Found'} product: {product.name}")
    
    return created_products

def create_admin_user():
    """Create superuser if it doesn't exist"""
    if not User.objects.filter(is_superuser=True).exists():
        admin = User.objects.create_superuser(
            email='admin@eshop.com',
            password='admin123456',
            first_name='Admin',
            last_name='User'
        )
        print(f"Created admin user: {admin.email}")
        return admin
    else:
        admin = User.objects.filter(is_superuser=True).first()
        print(f"Admin user already exists: {admin.email}")
        return admin

def main():
    """Main function to populate database"""
    print("🚀 Populating e-commerce database...")
    
    # Create categories
    print("\n📁 Creating categories...")
    categories = create_categories()
    
    # Create products
    print("\n📦 Creating products...")
    products = create_products(categories)
    
    # Create admin user
    print("\n👤 Creating admin user...")
    admin = create_admin_user()
    
    print(f"\n✅ Database populated successfully!")
    print(f"   Categories: {len(categories)}")
    print(f"   Products: {len(products)}")
    print(f"   Admin user: {admin.email} / admin123456")
    print(f"\n🌐 Visit your site and admin panel to see the data!")

if __name__ == '__main__':
    main()