# 🔍 Troubleshooting: Empty Pages / No Products Showing

## Issue: "I don't see anything"

This guide will help you diagnose why products or cart pages appear empty.

---

## Step 1: Check if Test Data Exists

Run this command:
```bash
python manage.py shell < check_data.py
```

**Expected Output:**
```
📊 Users: 1
   - admin@example.com (Admin: True)
📁 Categories: 1
   - Electronics (Active: True)
📦 Products: 4
   - iPhone 15 Pro
   - MacBook Air M3
   - AirPods Pro 2
   - iPad Air
```

**If you see "NO PRODUCTS FOUND":**
```bash
python manage.py shell < create_test_data.py
```

---

## Step 2: Check Server Console for Errors

Look at your terminal where the server is running. Check for:

❌ **Template errors**:
```
TemplateSyntaxError at /products/
```

❌ **Import errors**:
```
ImportError: No module named 'X'
```

❌ **Database errors**:
```
OperationalError: no such table
```

---

## Step 3: Check Browser Console (F12)

Open DevTools (F12) and check:

1. **Console Tab** - Look for JavaScript errors
2. **Network Tab** - Check if requests are returning 200 OK
3. **Elements Tab** - Check if HTML is being rendered

---

## Step 4: Verify URLs

Test each URL manually:

### Homepage
```
http://127.0.0.1:8000/
```
**Should show:** Welcome message + featured products

### Products List
```
http://127.0.0.1:8000/products/
```
**Should show:** Grid of 4 products

### Cart (empty)
```
http://127.0.0.1:8000/cart/
```
**Should show:** "Cart is empty" message

### Admin Panel
```
http://127.0.0.1:8000/admin/
```
**Should show:** Django admin login

---

## Step 5: Check Product Status in Admin

1. Visit: http://127.0.0.1:8000/admin/
2. Login: admin@example.com / admin123
3. Click "Products"
4. Verify each product has:
   - ✅ Status = "Active"
   - ✅ Is featured = checked (for homepage)
   - ✅ Stock > 0

---

## Step 6: Check Template Language

The templates use Django's i18n system. Make sure:

1. Your browser language preference
2. The language cookie is set
3. Translation files are compiled (if using .po files)

**Quick fix:** Switch language using the dropdown in navbar (繁中 ↔ EN)

---

## Step 7: Clear Browser Cache

Sometimes cached files cause issues:

1. Press `Ctrl + Shift + R` (hard refresh)
2. Or clear browser cache completely
3. Close and reopen browser

---

## Step 8: Restart Development Server

Stop the server (`Ctrl + C`) and restart:

```bash
python manage.py runserver --settings=eshop.settings.development
```

---

## Common Issues & Solutions

### Issue: "Page is blank/white"

**Cause:** Template rendering error or missing CSS

**Solution:**
1. Check server console for template errors
2. Verify Tailwind CDN is loading (check Network tab in DevTools)
3. Check if `{% extends "base.html" %}` is correct

---

### Issue: "Products exist in admin but not on frontend"

**Cause:** Product status is not "active"

**Solution:**
1. Go to admin → Products
2. For each product, set Status = "Active"
3. Save and refresh frontend

---

### Issue: "Images not showing"

**Cause:** MEDIA_URL not configured or images not uploaded

**Solution:**
1. In development, this is normal (gray placeholders)
2. To add images: go to admin → Products → Edit → Upload images
3. Check settings.py has `MEDIA_URL` and `MEDIA_ROOT`

---

### Issue: "Add to cart doesn't work"

**Cause:** JavaScript error or CSRF token missing

**Solution:**
1. Open DevTools Console - check for errors
2. Verify CSRF token in form (view page source)
3. Check server response in Network tab

---

### Issue: "404 Not Found on products/"

**Cause:** URLs not properly configured

**Solution:**
1. Verify `products/urls.py` exists
2. Check `products` app is in `INSTALLED_APPS`
3. Verify main `urls.py` includes `path("products/", include('products.urls'))`

---

## Quick Diagnostic Script

Save this as `diagnose.py` and run: `python manage.py shell < diagnose.py`

```python
from products.models import Product, Category
from cart.models import Cart
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("QUICK DIAGNOSTIC")
print("="*60)

# Check basics
print(f"\n✓ Users: {User.objects.count()}")
print(f"✓ Categories: {Category.objects.count()}")
print(f"✓ Products (total): {Product.objects.count()}")
print(f"✓ Products (active): {Product.objects.filter(status='active').count()}")
print(f"✓ Products (featured): {Product.objects.filter(is_featured=True).count()}")
print(f"✓ Carts: {Cart.objects.count()}")

# Check if any products are active and have images
active_products = Product.objects.filter(status='active')
if active_products.exists():
    print("\n📦 Sample Active Product:")
    p = active_products.first()
    print(f"   Name: {p.name_en}")
    print(f"   Price: NT$ {p.price:,}")
    print(f"   Stock: {p.stock}")
    print(f"   Images: {p.images.count()}")
    print(f"   Variants: {p.variants.count()}")
else:
    print("\n⚠️  NO ACTIVE PRODUCTS!")
    print("   Run: python manage.py shell < create_test_data.py")

print("\n" + "="*60)
```

---

## Still Having Issues?

1. **Check this file for errors:** `products/models.py`
2. **Verify migrations ran:** `python manage.py showmigrations`
3. **Check settings:** `INSTALLED_APPS` includes 'products', 'cart'
4. **Test in a different browser** (to rule out cache issues)

---

## Expected Working Flow

1. **Create test data** → Products exist in database
2. **Server running** → Can access URLs
3. **Visit /products/** → See product grid
4. **Click product** → See product details
5. **Add to cart** → Cart count increases
6. **Visit /cart/** → See cart items

If any step fails, that's where the issue is!

---

**Last Updated:** October 4, 2025