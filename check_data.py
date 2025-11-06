"""
Check if test data exists and verify cart functionality.
Run with: python manage.py shell < check_data.py
"""
from products.models import Category, Product, ProductVariant
from cart.models import Cart, CartItem
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("DATABASE STATUS CHECK")
print("=" * 60)

# Check users
user_count = User.objects.count()
print(f"\n📊 Users: {user_count}")
if user_count > 0:
    for user in User.objects.all()[:3]:
        print(f"   - {user.email} (Admin: {user.is_superuser})")

# Check categories
category_count = Category.objects.count()
print(f"\n📁 Categories: {category_count}")
if category_count > 0:
    for cat in Category.objects.all():
        print(f"   - {cat.name_en} (Active: {cat.is_active})")

# Check products
product_count = Product.objects.count()
print(f"\n📦 Products: {product_count}")
if product_count > 0:
    for product in Product.objects.all():
        print(f"   - {product.name_en}")
        print(f"     SKU: {product.sku}")
        print(f"     Price: NT$ {product.price:,}")
        if product.sale_price:
            print(f"     Sale: NT$ {product.sale_price:,}")
        print(f"     Stock: {product.stock}")
        print(f"     Status: {product.status}")
        print(f"     Featured: {product.is_featured}")
        
        # Check variants
        variants = product.variants.all()
        if variants.exists():
            print(f"     Variants: {variants.count()}")
            for v in variants:
                print(f"       - {v.name_en} (Stock: {v.stock})")
        print()

# Check carts
cart_count = Cart.objects.count()
print(f"🛒 Carts: {cart_count}")
if cart_count > 0:
    for cart in Cart.objects.all():
        items = cart.items.count()
        print(f"   - User: {cart.user.email if cart.user else 'Guest'}")
        print(f"     Items: {items}")

print("\n" + "=" * 60)

if product_count == 0:
    print("⚠️  NO PRODUCTS FOUND!")
    print("Run: python manage.py shell < create_test_data.py")
else:
    print("✅ Test data exists!")
    print("\n🔗 Visit: http://127.0.0.1:8000/products/")

print("=" * 60)