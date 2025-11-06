"""
Quick diagnostic to check system status
Run: python manage.py shell < diagnose.py
"""
from products.models import Product, Category
from cart.models import Cart
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("QUICK DIAGNOSTIC CHECK")
print("="*60)

# Check database
print(f"\n✓ Users: {User.objects.count()}")
print(f"✓ Categories: {Category.objects.count()}")
print(f"✓ Products (total): {Product.objects.count()}")
print(f"✓ Products (active): {Product.objects.filter(status='active').count()}")
print(f"✓ Products (featured): {Product.objects.filter(is_featured=True).count()}")
print(f"✓ Carts: {Cart.objects.count()}")

# Check active products
active_products = Product.objects.filter(status='active')
if active_products.exists():
    print("\n📦 Active Products Found:")
    for p in active_products:
        print(f"   - {p.name_en} (Stock: {p.stock}, Price: NT${p.price})")
        print(f"     Status: {p.status}, Featured: {p.is_featured}")
        print(f"     Images: {p.images.count()}, Variants: {p.variants.count()}")
else:
    print("\n⚠️  WARNING: NO ACTIVE PRODUCTS!")
    print("   Solution: Run 'python manage.py shell < create_test_data.py'")

print("\n" + "="*60)
print("\n🔗 Test These URLs:")
print("   http://127.0.0.1:8000/ (Homepage)")
print("   http://127.0.0.1:8000/products/ (Product List)")
print("   http://127.0.0.1:8000/cart/ (Shopping Cart)")
print("   http://127.0.0.1:8000/admin/ (Admin Panel)")
print("\n" + "="*60)