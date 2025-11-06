"""
Create test data for cart workflow testing.
Run with: python manage.py shell < create_test_data.py
"""
from products.models import Category, Product, ProductImage, ProductVariant
from django.contrib.auth import get_user_model

User = get_user_model()

print("Starting test data creation...")
print("=" * 60)

# 1. Create admin user
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='Test',
        preferred_language='en'
    )
    print("✅ Created admin account:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
else:
    print("ℹ️  Admin account already exists")

print()

# 2. Create category
category, created = Category.objects.get_or_create(
    slug='electronics',
    defaults={
        'name': '電子產品',
        'name_en': 'Electronics',
        'description': '各種優質電子產品',
        'description_en': 'Various quality electronic products',
        'is_active': True
    }
)
if created:
    print(f"✅ Created category: {category.name_en}")
else:
    print(f"ℹ️  Category already exists: {category.name_en}")

print()

# 3. Create products
products_data = [
    {
        'name': 'iPhone 15 Pro',
        'name_en': 'iPhone 15 Pro',
        'slug': 'iphone-15-pro',
        'sku': 'IP15P-001',
        'price': 35900,
        'sale_price': 33900,
        'stock': 50,
        'description': '最新款 iPhone 15 Pro，搭載革命性的 A17 Pro 晶片',
        'description_en': 'Latest iPhone 15 Pro with revolutionary A17 Pro chip. Titanium design for strength and lightness.',
        'has_variants': True,
    },
    {
        'name': 'MacBook Air M3',
        'name_en': 'MacBook Air M3',
        'slug': 'macbook-air-m3',
        'sku': 'MBA-M3-001',
        'price': 39900,
        'sale_price': None,
        'stock': 30,
        'description': '全新 M3 晶片，超薄設計，續航力可達 18 小時',
        'description_en': 'All-new M3 chip, ultra-thin design, up to 18 hours battery life. Perfect for work and entertainment.',
        'has_variants': False,
    },
    {
        'name': 'AirPods Pro 2',
        'name_en': 'AirPods Pro 2',
        'slug': 'airpods-pro-2',
        'sku': 'APP2-001',
        'price': 7490,
        'sale_price': 6990,
        'stock': 100,
        'description': '第二代 AirPods Pro，搭載主動降噪功能',
        'description_en': '2nd generation AirPods Pro with Active Noise Cancellation for immersive audio experience.',
        'has_variants': False,
    },
    {
        'name': 'iPad Air',
        'name_en': 'iPad Air',
        'slug': 'ipad-air',
        'sku': 'IPAD-AIR-001',
        'price': 19900,
        'sale_price': 18900,
        'stock': 5,  # Low stock for testing
        'description': '輕薄強大的 iPad Air，搭載 M1 晶片',
        'description_en': 'Powerful and lightweight iPad Air with M1 chip for creativity and entertainment.',
        'has_variants': False,
    },
]

print("Creating products:")
for product_data in products_data:
    has_variants = product_data.pop('has_variants')
    product, created = Product.objects.get_or_create(
        sku=product_data['sku'],
        defaults={
            **product_data,
            'category': category,
            'status': 'active',
            'is_featured': True,
            'weight': 0.5,
        }
    )
    
    if created:
        print(f"  ✅ {product.name_en}")
        print(f"     Price: NT$ {product.price:,}")
        if product.sale_price:
            discount = product.price - product.sale_price
            print(f"     Sale: NT$ {product.sale_price:,} (Save NT$ {discount:,})")
        print(f"     Stock: {product.stock} units")
        
        # Create color variants for iPhone
        if has_variants and 'iPhone' in product.name:
            colors = [
                ('鈦金屬', 'Titanium', 'IP15P-TITANIUM', 0),
                ('藍色鈦金屬', 'Blue Titanium', 'IP15P-BLUE', 0),
                ('白色鈦金屬', 'White Titanium', 'IP15P-WHITE', 0),
                ('黑色鈦金屬', 'Black Titanium', 'IP15P-BLACK', 0),
            ]
            print(f"     Creating variants:")
            for name_zh, name_en, sku, price_diff in colors:
                variant = ProductVariant.objects.create(
                    product=product,
                    name=name_zh,
                    name_en=name_en,
                    sku=sku,
                    price_difference=price_diff,
                    stock=15
                )
                print(f"       - {name_en} (Stock: 15)")
        print()
    else:
        print(f"  ℹ️  {product.name_en} (already exists)")

print("=" * 60)
print("✅ Test data creation complete!")
print()
print("🔗 You can now visit:")
print("   Admin Panel: http://127.0.0.1:8000/admin/")
print("   Email: admin@example.com")
print("   Password: admin123")
print()
print("   Product List: http://127.0.0.1:8000/products/")
print("   Shopping Cart: http://127.0.0.1:8000/cart/")
print("   Homepage: http://127.0.0.1:8000/")
print("=" * 60)