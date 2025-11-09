"""
Script to assign product images to products
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.development')
django.setup()

from products.models import Product, ProductImage

# Mapping of product slugs to image filenames
image_mappings = {
    'usda-1855-beef-short-ribs': '1855.jpg',
    'usda-choice-ribeye': 'angus.jpg',
    'taiwan-1983-pork-shoulder': 'kurubota.jpg',
    'hualien-wild-grouper': 'mutton.jpg',  # Using mutton as placeholder for fish
    'free-range-whole-chicken': 'pork_shoulder.jpg',  # Using as placeholder
    'taiwan-black-pork-belly': 'pork_shoulder.jpg',
}

# Alternative: Map based on product names
name_mappings = {
    '美國1855頂級牛小排': 'short_ribs.jpg',
    '美國Choice級牛肋眼': 'shoulder.jpg',
    '台灣1983神豬梅花肉': 'pork_shoulder.jpg',
    '花蓮野生石斑魚': 'mutton.jpg',
    '土雞全雞': 'kurubota.jpg',
    '台灣黑豬五花肉': 'pork_shoulder.jpg',
}

print("Assigning images to products...")
print("=" * 50)

for product in Product.objects.all():
    # Skip if product already has images
    if product.images.exists():
        print(f"✓ {product.name} - Already has images")
        continue
    
    # Try to find image for this product
    image_filename = name_mappings.get(product.name) or image_mappings.get(product.slug)
    
    if image_filename:
        image_path = f'products/2025/11/{image_filename}'
        
        # Create ProductImage entry
        product_image = ProductImage.objects.create(
            product=product,
            image=image_path,
            alt_text=product.name,
            display_order=1,
            is_primary=True
        )
        print(f"✓ {product.name} - Assigned: {image_filename}")
    else:
        print(f"✗ {product.name} - No image mapping found")

print("=" * 50)
print("\nImage assignment complete!")

# Show summary
products_with_images = Product.objects.filter(images__isnull=False).distinct().count()
total_products = Product.objects.count()
print(f"\nProducts with images: {products_with_images}/{total_products}")
