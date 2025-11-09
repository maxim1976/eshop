"""
Simple web endpoint to populate database data.
Access this via /populate_now/ in your browser when logged in as admin.
"""

from django.shortcuts import HttpResponse, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from products.models import Category, Product
import random

User = get_user_model()

@staff_member_required
def populate_now(request):
    """Web endpoint to populate database - only accessible by admin users."""
    
    if request.method == 'POST':
        # Do the actual population
        try:
            # Create categories
            categories_data = [
                {'name': '美國安格斯牛肉', 'name_en': 'American Angus Beef', 'slug': 'american-angus', 'display_order': 1},
                {'name': '台灣優質豬肉', 'name_en': 'Taiwan Premium Pork', 'slug': 'taiwan-premium', 'display_order': 2},
                {'name': '新鮮海鮮', 'name_en': 'Fresh Seafood', 'slug': 'seafood', 'display_order': 3},
                {'name': '雞肉產品', 'name_en': 'Poultry Products', 'slug': 'poultry', 'display_order': 4},
                {'name': '加工製品', 'name_en': 'Processed Foods', 'slug': 'processed', 'display_order': 5},
                {'name': '冷凍食品', 'name_en': 'Frozen Foods', 'slug': 'frozen', 'display_order': 6},
            ]
            
            created_categories = []
            for cat_data in categories_data:
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
            
            # Create products
            products_data = [
                {
                    'name': '美國安格斯牛排',
                    'name_en': 'American Angus Steak',
                    'slug': 'american-angus-steak',
                    'sku': 'BEEF-ANGUS-001',
                    'category': 'american-angus',
                    'description': '頂級美國安格斯牛排，肉質鮮嫩多汁',
                    'description_en': 'Premium American Angus steak, tender and juicy',
                    'price': 800,
                    'weight': 300,
                    'is_featured': True,
                },
                {
                    'name': '美國安格斯牛小排',
                    'name_en': 'American Angus Short Ribs',
                    'slug': 'american-angus-short-ribs',
                    'sku': 'BEEF-ANGUS-002',
                    'category': 'american-angus',
                    'description': '美國安格斯牛小排，適合燉煮',
                    'description_en': 'American Angus short ribs, perfect for braising',
                    'price': 650,
                    'weight': 500,
                    'is_featured': True,
                },
                {
                    'name': '台灣黑豬肉片',
                    'name_en': 'Taiwan Black Pork Slices',
                    'slug': 'taiwan-black-pork-slices',
                    'sku': 'PORK-BLACK-003',
                    'category': 'taiwan-premium',
                    'description': '台灣本土黑豬肉片，肉質甜美',
                    'description_en': 'Taiwan native black pork slices, sweet and tender',
                    'price': 350,
                    'weight': 400,
                    'is_featured': True,
                },
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
                {
                    'name': '美國安格斯牛肩胛肉',
                    'name_en': 'American Angus Chuck',
                    'slug': 'american-angus-chuck',
                    'sku': 'BEEF-ANGUS-008',
                    'category': 'american-angus',
                    'description': '美國安格斯牛肩胛肉，適合燉煮',
                    'description_en': 'American Angus chuck, perfect for slow cooking',
                    'price': 450,
                    'weight': 600,
                    'is_featured': True,
                },
            ]
            
            # Get categories by slug for easy lookup
            cat_lookup = {cat.slug: cat for cat in created_categories}
            
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
                        'stock': random.randint(10, 50),
                    }
                )
                created_products.append(product)
            
            return HttpResponse(f"""
                <html>
                <head><title>Database Populated!</title></head>
                <body style="font-family: Arial; padding: 40px; background: #f0f8ff;">
                    <h1 style="color: #28a745;">✅ Database Populated Successfully!</h1>
                    <p><strong>Categories created:</strong> {len(created_categories)}</p>
                    <p><strong>Products created:</strong> {len(created_products)}</p>
                    <hr>
                    <p><a href="/">📱 Visit Homepage</a></p>
                    <p><a href="/admin/">⚙️ Back to Admin</a></p>
                </body>
                </html>
            """)
            
        except Exception as e:
            return HttpResponse(f"""
                <html>
                <head><title>Error</title></head>
                <body style="font-family: Arial; padding: 40px; background: #ffe6e6;">
                    <h1 style="color: #dc3545;">❌ Error Populating Database</h1>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <p><a href="/populate_now/">🔄 Try Again</a></p>
                    <p><a href="/admin/">⚙️ Back to Admin</a></p>
                </body>
                </html>
            """)
    
    else:
        # Show the form
        categories_count = Category.objects.count()
        products_count = Product.objects.count()
        
        return HttpResponse(f"""
            <html>
            <head><title>Populate Database</title></head>
            <body style="font-family: Arial; padding: 40px; background: #f8f9fa;">
                <h1>🗃️ Database Population Tool</h1>
                <p><strong>Current Status:</strong></p>
                <ul>
                    <li>Categories: {categories_count}</li>
                    <li>Products: {products_count}</li>
                </ul>
                
                <form method="post" style="margin-top: 30px;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE')}">
                    <button type="submit" style="
                        background: #007bff; 
                        color: white; 
                        border: none; 
                        padding: 12px 24px; 
                        border-radius: 4px; 
                        font-size: 16px;
                        cursor: pointer;
                    ">
                        🚀 Populate Database Now
                    </button>
                </form>
                
                <p style="margin-top: 30px;">
                    <a href="/admin/">⚙️ Back to Admin</a>
                </p>
            </body>
            </html>
        """)