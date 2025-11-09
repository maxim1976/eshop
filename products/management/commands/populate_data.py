"""
Django management command to populate the database with initial data.
This can be run on Railway using: railway run python manage.py populate_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with initial categories and products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Clearing existing data...')
            Product.objects.all().delete()
            Category.objects.all().delete()

        self.stdout.write('🚀 Populating e-commerce database...')
        
        # Create categories
        self.stdout.write('\n📁 Creating categories...')
        categories = self.create_categories()
        
        # Create products
        self.stdout.write('\n📦 Creating products...')
        products = self.create_products(categories)
        
        # Create admin user
        self.stdout.write('\n👤 Creating admin user...')
        admin = self.create_admin_user()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Database populated successfully!')
        )
        self.stdout.write(f'   Categories: {len(categories)}')
        self.stdout.write(f'   Products: {len(products)}')
        self.stdout.write(f'   Admin user: {admin.email}')
        self.stdout.write(f'\n🌐 Visit your site and admin panel to see the data!')

    def create_categories(self):
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
            self.stdout.write(f"{'✓ Created' if created else '○ Found'} category: {category.name}")
        
        return created_categories

    def create_products(self, categories):
        """Create sample products"""
        products_data = [
            # American Angus Beef
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
            # Taiwan Premium Pork
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
                'name': '台灣豬五花肉',
                'name_en': 'Taiwan Pork Belly',
                'slug': 'taiwan-pork-belly',
                'sku': 'PORK-BELLY-004',
                'category': 'taiwan-premium',
                'description': '新鮮台灣豬五花肉，油脂豐富',
                'description_en': 'Fresh Taiwan pork belly, rich and fatty',
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
            # Additional featured products to reach at least 6
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
            {
                'name': '台灣豬絞肉',
                'name_en': 'Taiwan Ground Pork',
                'slug': 'taiwan-ground-pork',
                'sku': 'PORK-GROUND-009',
                'category': 'taiwan-premium',
                'description': '新鮮台灣豬絞肉，料理萬用',
                'description_en': 'Fresh Taiwan ground pork, versatile for cooking',
                'price': 200,
                'weight': 300,
                'is_featured': True,
            },
            {
                'name': '新鮮鮭魚',
                'name_en': 'Fresh Salmon',
                'slug': 'fresh-salmon',
                'sku': 'SEAFOOD-SALMON-010',
                'category': 'seafood',
                'description': '新鮮鮭魚，富含Omega-3',
                'description_en': 'Fresh salmon, rich in Omega-3',
                'price': 520,
                'weight': 400,
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
                    'stock': random.randint(10, 50),
                }
            )
            created_products.append(product)
            self.stdout.write(f"{'✓ Created' if created else '○ Found'} product: {product.name}")
        
        return created_products

    def create_admin_user(self):
        """Create superuser if it doesn't exist"""
        admin_email = 'admin@eshop.com'
        
        if not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create_superuser(
                email=admin_email,
                password='admin123456',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f"✓ Created admin user: {admin.email}")
            self.stdout.write(f"  Password: admin123456")
            return admin
        else:
            admin = User.objects.filter(email=admin_email).first()
            self.stdout.write(f"○ Admin user already exists: {admin.email}")
            return admin