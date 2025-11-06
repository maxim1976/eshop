"""
Management command to create sample product data for testing.
Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductVariant
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample product data for testing the e-commerce platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sample data creation...'))
        self.stdout.write('=' * 60)

        # Create admin user if doesn't exist
        if not User.objects.filter(email='admin@example.com').exists():
            admin_user = User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                preferred_language='en'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin user created'))
            self.stdout.write(f'   Email: admin@example.com')
            self.stdout.write(f'   Password: admin123')
        else:
            self.stdout.write(self.style.WARNING('ℹ️  Admin user already exists'))

        # Create Electronics category
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
            self.stdout.write(self.style.SUCCESS(f'✅ Category created: {category.name_en}'))
        else:
            self.stdout.write(self.style.WARNING(f'ℹ️  Category exists: {category.name_en}'))

        # Sample products data
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'name_en': 'iPhone 15 Pro',
                'slug': 'iphone-15-pro',
                'sku': 'IP15P-001',
                'price': Decimal('35900.00'),
                'sale_price': Decimal('33900.00'),
                'stock': 50,
                'description': '最新款 iPhone 15 Pro，搭載革命性的 A17 Pro 晶片，鈦金屬設計更輕更堅固。',
                'description_en': 'Latest iPhone 15 Pro with revolutionary A17 Pro chip. Titanium design for strength and lightness.',
                'meta_title_en': 'iPhone 15 Pro - Premium Smartphone',
                'meta_description_en': 'Experience the power of A17 Pro chip with titanium design',
                'weight': Decimal('0.187'),
                'has_variants': True,
            },
            {
                'name': 'MacBook Air M3',
                'name_en': 'MacBook Air M3',
                'slug': 'macbook-air-m3',
                'sku': 'MBA-M3-001',
                'price': Decimal('39900.00'),
                'sale_price': None,
                'stock': 30,
                'description': '全新 M3 晶片，超薄設計，續航力可達 18 小時。完美的工作與娛樂夥伴。',
                'description_en': 'All-new M3 chip, ultra-thin design, up to 18 hours battery life. Perfect for work and entertainment.',
                'meta_title_en': 'MacBook Air M3 - Lightweight Laptop',
                'meta_description_en': 'Ultra-portable laptop with M3 chip and all-day battery',
                'weight': Decimal('1.24'),
                'has_variants': False,
            },
            {
                'name': 'AirPods Pro 2',
                'name_en': 'AirPods Pro 2',
                'slug': 'airpods-pro-2',
                'sku': 'APP2-001',
                'price': Decimal('7490.00'),
                'sale_price': Decimal('6990.00'),
                'stock': 100,
                'description': '第二代 AirPods Pro，搭載主動降噪功能，提供身臨其境的音訊體驗。',
                'description_en': '2nd generation AirPods Pro with Active Noise Cancellation for immersive audio experience.',
                'meta_title_en': 'AirPods Pro 2 - Wireless Earbuds',
                'meta_description_en': 'Premium wireless earbuds with active noise cancellation',
                'weight': Decimal('0.056'),
                'has_variants': False,
            },
            {
                'name': 'iPad Air',
                'name_en': 'iPad Air',
                'slug': 'ipad-air',
                'sku': 'IPAD-AIR-001',
                'price': Decimal('19900.00'),
                'sale_price': Decimal('18900.00'),
                'stock': 5,
                'description': '輕薄強大的 iPad Air，搭載 M1 晶片，適合創作和娛樂。',
                'description_en': 'Powerful and lightweight iPad Air with M1 chip for creativity and entertainment.',
                'meta_title_en': 'iPad Air - Versatile Tablet',
                'meta_description_en': 'Lightweight tablet with M1 chip for work and play',
                'weight': Decimal('0.461'),
                'has_variants': False,
            },
        ]

        self.stdout.write('\nCreating products:')
        for product_data in products_data:
            has_variants = product_data.pop('has_variants')
            
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults={
                    **product_data,
                    'category': category,
                    'status': 'active',
                    'is_featured': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {product.name_en}'))
                self.stdout.write(f'     Price: NT$ {product.price:,}')
                if product.sale_price:
                    discount = product.price - product.sale_price
                    self.stdout.write(f'     Sale: NT$ {product.sale_price:,} (Save NT$ {discount:,})')
                self.stdout.write(f'     Stock: {product.stock} units')
                
                # Create variants for iPhone
                if has_variants and 'iPhone' in product.name_en:
                    self.stdout.write('     Creating variants:')
                    variants_data = [
                        ('鈦金屬', 'Titanium', 'IP15P-TITANIUM'),
                        ('藍色鈦金屬', 'Blue Titanium', 'IP15P-BLUE'),
                        ('白色鈦金屬', 'White Titanium', 'IP15P-WHITE'),
                        ('黑色鈦金屬', 'Black Titanium', 'IP15P-BLACK'),
                    ]
                    for name_zh, name_en, sku in variants_data:
                        variant = ProductVariant.objects.create(
                            product=product,
                            name=name_zh,
                            name_en=name_en,
                            sku=sku,
                            price_difference=Decimal('0.00'),
                            stock=15
                        )
                        self.stdout.write(f'       - {name_en} (Stock: 15)')
            else:
                self.stdout.write(self.style.WARNING(f'  ℹ️  {product.name_en} (already exists)'))

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Sample data creation complete!'))
        self.stdout.write('\n🔗 You can now visit:')
        self.stdout.write('   Admin Panel: http://127.0.0.1:8000/admin/')
        self.stdout.write('   Email: admin@example.com')
        self.stdout.write('   Password: admin123')
        self.stdout.write('\n   Product List: http://127.0.0.1:8000/products/')
        self.stdout.write('   Shopping Cart: http://127.0.0.1:8000/cart/')
        self.stdout.write('   Homepage: http://127.0.0.1:8000/')
        self.stdout.write('=' * 60)