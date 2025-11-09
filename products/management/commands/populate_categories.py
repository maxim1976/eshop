"""
Management command to populate product categories.
Usage: python manage.py populate_categories
"""
from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Populate product categories for EShop'

    def handle(self, *args, **options):
        self.stdout.write('Creating product categories...')
        
        categories_data = [
            {
                'name': '美國1855',
                'name_en': 'American 1855',
                'slug': 'american-beef',
                'description': '嚴選美國1855頂級牛肉，品質保證',
                'description_en': 'Premium American 1855 beef, quality guaranteed',
                'display_order': 1,
            },
            {
                'name': '牛肉類',
                'name_en': 'Beef',
                'slug': 'beef',
                'description': '新鮮優質牛肉，各式部位',
                'description_en': 'Fresh quality beef, various cuts',
                'display_order': 2,
            },
            {
                'name': '羊肉類',
                'name_en': 'Lamb',
                'slug': 'lamb',
                'description': '新鮮羊肉，適合各式料理',
                'description_en': 'Fresh lamb, suitable for various dishes',
                'display_order': 3,
            },
            {
                'name': '雞肉類',
                'name_en': 'Chicken',
                'slug': 'chicken',
                'description': '新鮮雞肉，健康首選',
                'description_en': 'Fresh chicken, healthy choice',
                'display_order': 4,
            },
            {
                'name': '台灣1983神豬',
                'name_en': 'Taiwan 1983 Premium Pork',
                'slug': 'taiwan-premium',
                'description': '台灣本土優質豬肉，健康安心',
                'description_en': 'Taiwan premium pork, healthy and safe',
                'display_order': 5,
            },
            {
                'name': '豬肉類',
                'name_en': 'Pork',
                'slug': 'pork',
                'description': '新鮮豬肉，各式部位',
                'description_en': 'Fresh pork, various cuts',
                'display_order': 6,
            },
            {
                'name': '海鮮類',
                'name_en': 'Seafood',
                'slug': 'seafood',
                'description': '新鮮海鮮，花蓮在地直送',
                'description_en': 'Fresh seafood, delivered from Hualien',
                'display_order': 7,
            },
            {
                'name': '其他類',
                'name_en': 'Others',
                'slug': 'others',
                'description': '其他肉品及加工食品',
                'description_en': 'Other meats and processed foods',
                'display_order': 8,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            category, created = Category.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created category: {category.name} ({category.name_en})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated category: {category.name} ({category.name_en})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Done! Created {created_count}, Updated {updated_count} categories'
            )
        )
        self.stdout.write(
            self.style.SUCCESS('Now categories will appear in the navigation menu!')
        )
