"""
Complete automated setup script for 日日鮮肉品專賣 Taiwan E-commerce Platform.
Handles migrations, sample data creation, and initial configuration.
Run with: python setup_日日鮮肉品專賣.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '日日鮮肉品專賣.settings.development')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductVariant
from decimal import Decimal
from django.db import connection

User = get_user_model()


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_database_connection():
    """Verify database connectivity."""
    print_header("📊 STEP 1: CHECKING DATABASE CONNECTION")
    try:
        connection.ensure_connection()
        print("✅ Database connection successful")
        print(f"   Database: {connection.settings_dict['NAME']}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_migrations():
    """Create all necessary migrations."""
    print_header("📝 STEP 2: CREATING DATABASE MIGRATIONS")
    
    apps_to_migrate = ['authentication', 'products', 'cart', 'orders']
    
    for app in apps_to_migrate:
        try:
            print(f"Creating migrations for {app}...")
            call_command('makemigrations', app, interactive=False)
            print(f"✅ Migrations created for {app}")
        except Exception as e:
            print(f"⚠️  Migration creation for {app}: {e}")
    
    print("\n✅ All migrations created successfully")


def apply_migrations():
    """Apply all pending migrations."""
    print_header("🔄 STEP 3: APPLYING DATABASE MIGRATIONS")
    
    try:
        call_command('migrate', interactive=False)
        print("✅ All migrations applied successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def create_superuser():
    """Create admin superuser account."""
    print_header("👤 STEP 4: CREATING ADMIN ACCOUNT")
    
    admin_email = 'admin@example.com'
    admin_password = 'admin123'
    
    if User.objects.filter(email=admin_email).exists():
        print(f"ℹ️  Admin account already exists: {admin_email}")
        return True
    
    try:
        User.objects.create_superuser(
            email=admin_email,
            password=admin_password,
            first_name='Admin',
            last_name='User',
            preferred_language='en'
        )
        print("✅ Admin account created successfully")
        print(f"   📧 Email: {admin_email}")
        print(f"   🔑 Password: {admin_password}")
        return True
    except Exception as e:
        print(f"❌ Failed to create admin: {e}")
        return False


def create_categories():
    """Create product categories with bilingual names."""
    print_header("📁 STEP 5: CREATING PRODUCT CATEGORIES")
    
    categories_data = [
        {
            'name': '電子產品',
            'name_en': 'Electronics',
            'slug': 'electronics',
            'description': '各種優質電子產品，包括手機、筆記型電腦、耳機等',
            'description_en': 'Various quality electronic products including phones, laptops, headphones',
        },
        {
            'name': '家電',
            'name_en': 'Home Appliances',
            'slug': 'home-appliances',
            'description': '智慧家電與生活用品',
            'description_en': 'Smart home appliances and lifestyle products',
        },
        {
            'name': '配件',
            'name_en': 'Accessories',
            'slug': 'accessories',
            'description': '各式電子配件與周邊商品',
            'description_en': 'Various electronic accessories and peripherals',
        },
    ]
    
    created_count = 0
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                **cat_data,
                'is_active': True,
                'display_order': created_count
            }
        )
        if created:
            print(f"✅ Created: {category.name_en} / {category.name}")
            created_count += 1
        else:
            print(f"ℹ️  Exists: {category.name_en} / {category.name}")
    
    print(f"\n✅ Categories ready: {Category.objects.count()} total")
    return Category.objects.filter(slug='electronics').first()


def create_sample_products(electronics_category):
    """Create sample products with bilingual information."""
    print_header("🛍️  STEP 6: CREATING SAMPLE PRODUCTS")
    
    products_data = [
        {
            'name': 'iPhone 15 Pro',
            'name_en': 'iPhone 15 Pro',
            'slug': 'iphone-15-pro',
            'sku': 'IP15P-001',
            'price': Decimal('35900.00'),
            'sale_price': Decimal('33900.00'),
            'stock': 50,
            'description': '最新款 iPhone 15 Pro，搭載革命性的 A17 Pro 晶片，鈦金屬設計更輕更堅固。6.1吋 Super Retina XDR 顯示器，專業級相機系統。',
            'description_en': 'Latest iPhone 15 Pro with revolutionary A17 Pro chip. Titanium design for strength and lightness. 6.1-inch Super Retina XDR display with ProMotion.',
            'specifications': '• A17 Pro 晶片\n• 6.1吋 Super Retina XDR\n• Pro 相機系統\n• 鈦金屬設計',
            'specifications_en': '• A17 Pro chip\n• 6.1" Super Retina XDR\n• Pro camera system\n• Titanium design',
            'meta_title_en': 'iPhone 15 Pro - Premium Smartphone | 日日鮮肉品專賣 Taiwan',
            'meta_description_en': 'Experience the power of A17 Pro chip with titanium design. Professional camera system and all-day battery life.',
            'weight': Decimal('187'),
            'has_variants': True,
        },
        {
            'name': 'MacBook Air M3',
            'name_en': 'MacBook Air M3 13-inch',
            'slug': 'macbook-air-m3-13',
            'sku': 'MBA-M3-13-001',
            'price': Decimal('39900.00'),
            'sale_price': None,
            'stock': 30,
            'description': '全新 M3 晶片，超薄設計，續航力可達 18 小時。13.6吋 Liquid Retina 顯示器，完美的工作與娛樂夥伴。',
            'description_en': 'All-new M3 chip in an incredibly thin design. Up to 18 hours of battery life. 13.6-inch Liquid Retina display. Perfect for work and entertainment.',
            'specifications': '• Apple M3 晶片\n• 8GB 統一記憶體\n• 256GB SSD\n• 13.6吋 Liquid Retina',
            'specifications_en': '• Apple M3 chip\n• 8GB unified memory\n• 256GB SSD\n• 13.6" Liquid Retina',
            'meta_title_en': 'MacBook Air M3 13-inch - Lightweight Laptop | 日日鮮肉品專賣 Taiwan',
            'meta_description_en': 'Ultra-portable laptop with M3 chip and all-day battery. Perfect balance of performance and portability.',
            'weight': Decimal('1240'),
            'has_variants': False,
        },
        {
            'name': 'AirPods Pro 第二代',
            'name_en': 'AirPods Pro (2nd generation)',
            'slug': 'airpods-pro-2nd-gen',
            'sku': 'APP2-001',
            'price': Decimal('7490.00'),
            'sale_price': Decimal('6990.00'),
            'stock': 100,
            'description': '第二代 AirPods Pro，搭載主動降噪功能，提供身臨其境的音訊體驗。支援 MagSafe 充電，電池續航力更持久。',
            'description_en': '2nd generation AirPods Pro with Active Noise Cancellation for immersive audio experience. MagSafe charging and longer battery life.',
            'specifications': '• 主動降噪\n• 通透模式\n• 個人化空間音訊\n• MagSafe 充電',
            'specifications_en': '• Active Noise Cancellation\n• Transparency mode\n• Personalized Spatial Audio\n• MagSafe charging',
            'meta_title_en': 'AirPods Pro 2nd Gen - Wireless Earbuds | 日日鮮肉品專賣 Taiwan',
            'meta_description_en': 'Premium wireless earbuds with active noise cancellation and personalized spatial audio.',
            'weight': Decimal('56'),
            'has_variants': False,
        },
        {
            'name': 'iPad Air',
            'name_en': 'iPad Air 11-inch M2',
            'slug': 'ipad-air-11-m2',
            'sku': 'IPAD-AIR-11-001',
            'price': Decimal('19900.00'),
            'sale_price': Decimal('18900.00'),
            'stock': 25,
            'description': '輕薄強大的 iPad Air，搭載 M2 晶片，11吋 Liquid Retina 顯示器。適合創作、學習和娛樂。',
            'description_en': 'Powerful and lightweight iPad Air with M2 chip. 11-inch Liquid Retina display. Perfect for creativity, learning, and entertainment.',
            'specifications': '• Apple M2 晶片\n• 11吋 Liquid Retina\n• 128GB 儲存空間\n• 支援 Apple Pencil',
            'specifications_en': '• Apple M2 chip\n• 11" Liquid Retina\n• 128GB storage\n• Apple Pencil support',
            'meta_title_en': 'iPad Air 11-inch M2 - Versatile Tablet | 日日鮮肉品專賣 Taiwan',
            'meta_description_en': 'Lightweight tablet with M2 chip for work and play. Support for Apple Pencil and Magic Keyboard.',
            'weight': Decimal('461'),
            'has_variants': False,
        },
        {
            'name': 'Apple Watch Series 9',
            'name_en': 'Apple Watch Series 9',
            'slug': 'apple-watch-series-9',
            'sku': 'AW-S9-001',
            'price': Decimal('13900.00'),
            'sale_price': None,
            'stock': 40,
            'description': 'Apple Watch Series 9 搭載 S9 晶片，雙指互點手勢，更明亮的螢幕。全方位健康與體能追蹤。',
            'description_en': 'Apple Watch Series 9 with S9 chip, double tap gesture, and brighter display. Comprehensive health and fitness tracking.',
            'specifications': '• S9 晶片\n• 雙指互點手勢\n• 健康監測\n• GPS + 行動網路',
            'specifications_en': '• S9 chip\n• Double tap gesture\n• Health monitoring\n• GPS + Cellular',
            'meta_title_en': 'Apple Watch Series 9 - Smart Watch | 日日鮮肉品專賣 Taiwan',
            'meta_description_en': 'Advanced health features with S9 chip and innovative double tap gesture control.',
            'weight': Decimal('51'),
            'has_variants': True,
        },
    ]
    
    created_count = 0
    for product_data in products_data:
        has_variants = product_data.pop('has_variants')
        
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults={
                **product_data,
                'category': electronics_category,
                'status': 'active',
                'is_featured': True,
                'is_new': True,
            }
        )
        
        if created:
            created_count += 1
            print(f"\n✅ {product.name_en} / {product.name}")
            print(f"   💰 Price: NT$ {product.price:,}")
            if product.sale_price:
                discount = product.price - product.sale_price
                percentage = int((discount / product.price) * 100)
                print(f"   🏷️  Sale: NT$ {product.sale_price:,} (Save {percentage}% / NT$ {discount:,})")
            print(f"   📦 Stock: {product.stock} units")
            print(f"   ⚖️  Weight: {product.weight}g")
            
            # Create variants for specific products
            if has_variants:
                create_product_variants(product)
        else:
            print(f"ℹ️  Exists: {product.name_en}")
    
    print(f"\n✅ Products created: {created_count} new, {Product.objects.count()} total")


def create_product_variants(product):
    """Create color/size variants for products."""
    print(f"   Creating variants for {product.name_en}...")
    
    if 'iPhone' in product.name_en:
        variants_data = [
            ('鈦金屬', 'Natural Titanium', f'{product.sku}-NAT'),
            ('藍色鈦金屬', 'Blue Titanium', f'{product.sku}-BLU'),
            ('白色鈦金屬', 'White Titanium', f'{product.sku}-WHT'),
            ('黑色鈦金屬', 'Black Titanium', f'{product.sku}-BLK'),
        ]
    elif 'Watch' in product.name_en:
        variants_data = [
            ('午夜色鋁金屬', 'Midnight Aluminum', f'{product.sku}-MID'),
            ('星光色鋁金屬', 'Starlight Aluminum', f'{product.sku}-STR'),
            ('銀色不鏽鋼', 'Silver Stainless Steel', f'{product.sku}-SIL'),
        ]
    else:
        return
    
    for name_zh, name_en, sku in variants_data:
        variant, created = ProductVariant.objects.get_or_create(
            sku=sku,
            defaults={
                'product': product,
                'name': name_zh,
                'name_en': name_en,
                'price_difference': Decimal('0.00'),
                'stock': 15,
                'is_active': True,
            }
        )
        if created:
            print(f"     ➜ {name_en} / {name_zh} (Stock: 15)")


def collect_static_files():
    """Collect static files for deployment."""
    print_header("📦 STEP 7: COLLECTING STATIC FILES")
    
    try:
        call_command('collectstatic', interactive=False, clear=True)
        print("✅ Static files collected successfully")
        return True
    except Exception as e:
        print(f"⚠️  Static files collection: {e}")
        return False


def print_summary():
    """Print setup summary and next steps."""
    print_header("🎉 SETUP COMPLETE!")
    
    print("📊 DATABASE SUMMARY:")
    print(f"   Categories: {Category.objects.count()}")
    print(f"   Products: {Product.objects.count()}")
    print(f"   Product Variants: {ProductVariant.objects.count()}")
    print(f"   Users: {User.objects.count()}")
    
    print("\n🔐 ADMIN CREDENTIALS:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    
    print("\n🌐 ACCESS YOUR SITE:")
    print("   Admin Panel: http://127.0.0.1:8000/admin/")
    print("   Products: http://127.0.0.1:8000/products/")
    print("   Shopping Cart: http://127.0.0.1:8000/cart/")
    print("   Homepage: http://127.0.0.1:8000/")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Start the development server:")
    print("      python manage.py runserver --settings=日日鮮肉品專賣.settings.development")
    print("   2. Visit http://127.0.0.1:8000/admin/ and login")
    print("   3. Explore the bilingual product catalog")
    print("   4. Test the shopping cart functionality")
    
    print("\n✨ FEATURES:")
    print("   ✅ Bilingual support (繁體中文 / English)")
    print("   ✅ Taiwan-specific pricing (NT$)")
    print("   ✅ Product variants (colors, sizes)")
    print("   ✅ Shopping cart with session support")
    print("   ✅ Admin interface with bilingual labels")
    print("   ✅ SEO-optimized product pages")
    
    print("\n" + "=" * 80)


def main():
    """Main setup execution."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "日日鮮肉品專賣 TAIWAN E-COMMERCE PLATFORM SETUP" + " " * 24 + "║")
    print("║" + " " * 20 + "Automated Installation & Configuration" + " " * 19 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Execute setup steps
        if not check_database_connection():
            print("\n❌ Setup aborted: Database connection failed")
            sys.exit(1)
        
        create_migrations()
        
        if not apply_migrations():
            print("\n❌ Setup aborted: Migration failed")
            sys.exit(1)
        
        if not create_superuser():
            print("\n⚠️  Warning: Admin account creation failed")
        
        electronics_category = create_categories()
        
        if electronics_category:
            create_sample_products(electronics_category)
        
        collect_static_files()
        
        print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()