# 🛒 Shopping Cart - Complete Testing Guide

## Overview
This guide will help you test the complete shopping cart functionality of your Taiwan e-commerce platform.

## Prerequisites

### 1️⃣ Create Test Data
```bash
# Run in terminal
python manage.py shell < create_test_data.py
```

**Expected Results:**
- ✅ Admin account created: admin@example.com / admin123
- ✅ Electronics category created
- ✅ 4 test products created (iPhone, MacBook, AirPods, iPad)
- ✅ 4 color variants created for iPhone

### 2️⃣ Start Development Server
```bash
python manage.py runserver --settings=日日鮮肉品專賣.settings.development
```

Visit: http://127.0.0.1:8000/

---

## Testing Workflow

### 📝 **Test 1: Browse Products**

**Steps:**
1. Visit homepage: http://127.0.0.1:8000/
2. Click "Products" in navigation
3. View product listing page

**Expected Results:**
- ✅ 4 product cards displayed
- ✅ Product images shown (or gray placeholders)
- ✅ Product names and prices visible
- ✅ "Sale" badges on iPhone, AirPods, and iPad
- ✅ "Low Stock" badge on iPad (only 5 units)
- ✅ "View Details" buttons work

---

### 🛍️ **Test 2: Add to Cart (Guest User)**

**Steps:**
1. Click any product to view details (suggest: AirPods Pro 2)
2. Review product information
3. Click "Add to Cart" button

**Expected Results:**
- ✅ No page reload (AJAX request)
- ✅ Success message appears: "Product added to cart"
- ✅ Cart badge in navbar shows "1"
- ✅ Button changes to "Added to Cart" (checkmark icon)

**Variations:**
1. Click "Add to Cart" again
   - ✅ Cart count increases to "2"
2. Add different product
   - ✅ Cart count accumulates

---

### 🎨 **Test 3: Product Variants (iPhone)**

**Steps:**
1. Visit iPhone 15 Pro product page
2. View variant options (Titanium, Blue, White, Black)
3. Select "Blue Titanium"
4. Click "Add to Cart"

**Expected Results:**
- ✅ Successfully added, cart count +1
- ✅ Cart shows "Variant: Blue Titanium"

**Variations:**
1. Try adding without selecting variant
   - ✅ Error message: "Please select a variant"
   - ✅ Variant dropdown highlighted in red

---

### 🛒 **Test 4: View Cart**

**Steps:**
1. Click cart icon in navbar
2. View cart page

**Expected Results:**
- ✅ All added products displayed
- ✅ Each item shows:
  - Product image
  - Product name (clickable link)
  - Variant (if applicable)
  - SKU
  - Unit price
  - Quantity controls (- number +)
  - Remove button
  - Subtotal
- ✅ Right sidebar shows order summary:
  - Item subtotal
  - Shipping fee (NT$ 100 if under NT$ 1,000)
  - Free shipping progress bar
  - Total
  - "Proceed to Checkout" button
  - "Continue Shopping" button

---

### ➕➖ **Test 5: Quantity Adjustment**

**Steps:**
1. On cart page
2. Click "+" button on any product
3. Click "-" button
4. Type a number directly in quantity field

**Expected Results:**
- ✅ Click "+": quantity increases by 1, no page reload
- ✅ Click "-": quantity decreases by 1 (minimum 1)
- ✅ Direct input: quantity updates
- ✅ Item subtotal updates instantly
- ✅ Total updates instantly
- ✅ Navbar cart count updates
- ✅ Free shipping progress updates

**Edge Cases:**
1. Increase quantity beyond stock
   - ✅ Error message: "Insufficient stock"
   - ✅ Quantity auto-adjusts to max available

2. Enter 0 or negative number
   - ✅ Auto-set to 1

---

### 🗑️ **Test 6: Remove Items**

**Steps:**
1. Click "Remove" button on any product
2. Confirm in dialog box

**Expected Results:**
- ✅ Confirmation dialog: "Are you sure you want to remove this item?"
- ✅ After confirming: item disappears from list
- ✅ Total updates
- ✅ Navbar cart count decreases
- ✅ If cart becomes empty: "Cart is empty" message appears

---

### 🧹 **Test 7: Clear Cart**

**Steps:**
1. Add multiple products
2. Click "Clear Cart" button
3. Confirm in dialog

**Expected Results:**
- ✅ Confirmation dialog: "Are you sure you want to clear the cart?"
- ✅ After confirming: all items removed
- ✅ Empty cart page displayed
- ✅ Navbar cart count shows "0"

---

### 📦 **Test 8: Free Shipping Calculation**

**Steps:**
1. Clear cart
2. Add 1 AirPods (NT$ 6,990)
3. Check shipping and progress

**Expected Results:**
- ✅ Item subtotal: NT$ 6,990
- ✅ Shipping: NT$ 100 (because under NT$ 1,000 threshold)
- ✅ Total: NT$ 7,090
- ✅ Progress bar shows ~70%
- ✅ Message: "Add NT$ XXX more for free shipping"

**Continue:**
1. Add another AirPods (total NT$ 13,980)
   - ✅ Shipping becomes "Free Shipping" (green text)
   - ✅ Total = Item subtotal
   - ✅ Progress bar at 100%
   - ✅ Free shipping message disappears

---

### ⚠️ **Test 9: Stock Warnings**

**Steps:**
1. Add iPad Air (only 5 units in stock)
2. View cart

**Expected Results:**
- ✅ Orange warning badge: "⚠️ Only 5 units remaining"

**Edge Cases:**
1. Try to set quantity to 6
   - ✅ Error: "Insufficient stock"
   - ✅ Quantity stays at 5

---

### 👤 **Test 10: Cart Merge After Login**

**Steps:**
1. As guest, add 2-3 products to cart
2. Login (admin@example.com / admin123)
3. View cart

**Expected Results:**
- ✅ Guest cart items automatically merged into user cart
- ✅ All products retained
- ✅ Quantities correctly accumulated (if same product added before/after login)
- ✅ Cart persists after logout/login

---

### 🌐 **Test 11: Language Switching**

**Steps:**
1. On cart page
2. Click language switcher (繁中 ↔ EN)

**Expected Results:**
- ✅ Page title switches language
- ✅ Button text switches
- ✅ Product names switch (if English name available)
- ✅ Messages switch
- ✅ Cart functionality continues working

---

### 📱 **Test 12: Responsive Design**

**Steps:**
1. Resize browser window
2. Test mobile (375px)
3. Test tablet (768px)
4. Test desktop (1024px+)

**Expected Results:**
- ✅ Mobile: single column layout, summary below items
- ✅ Tablet: appropriate spacing
- ✅ Desktop: items list + sidebar summary
- ✅ All buttons clickable on all sizes
- ✅ Text remains readable

---

### 🔒 **Test 13: Security**

**Steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Perform cart operations (add, update, remove)

**Expected Results:**
- ✅ All POST requests include CSRF token
- ✅ No 403 Forbidden errors
- ✅ Error messages don't leak sensitive info
- ✅ Can't modify other users' cart items

---

### ⚡ **Test 14: Performance**

**Steps:**
1. Add 10+ different products
2. Check cart page load time
3. Test quantity update speed

**Expected Results:**
- ✅ Page load < 2 seconds
- ✅ AJAX update response < 500ms
- ✅ No noticeable lag or freezing

---

## 🐛 Troubleshooting

### Issue 1: Cart count not updating
**Solution:**
- Check `cart/context_processors.py` is registered in settings
- Clear browser cache
- Check console for JavaScript errors

### Issue 2: CSRF token errors
**Solution:**
- Ensure `{% csrf_token %}` in all forms
- Check JavaScript reads `csrftoken` cookie correctly
- Verify CSRF settings in settings.py

### Issue 3: Images not showing
**Solution:**
- Check `MEDIA_URL` and `MEDIA_ROOT` settings
- Ensure development URLs include media serving
- Upload test images in admin

### Issue 4: Guest cart not working
**Solution:**
- Check session configuration
- Verify `SESSION_ENGINE` settings
- Clear browser cookies

---

## ✅ Testing Completion Checklist

After completing all tests, verify:

- [ ] ✅ Can browse products
- [ ] ✅ Can add to cart (guest + logged in)
- [ ] ✅ Can select product variants
- [ ] ✅ Can view cart
- [ ] ✅ Can adjust quantities
- [ ] ✅ Can remove items
- [ ] ✅ Can clear cart
- [ ] ✅ Free shipping calculation works
- [ ] ✅ Stock warnings display
- [ ] ✅ Cart merges after login
- [ ] ✅ Language switching works
- [ ] ✅ Responsive design good
- [ ] ✅ CSRF protection enabled
- [ ] ✅ Performance acceptable

---

## 🎉 All Tests Passed!

If all tests pass, congratulations! Your shopping cart system is fully functional!

**Next Steps:**
- [ ] Implement checkout flow
- [ ] Integrate payment gateway
- [ ] Order management
- [ ] Email notifications
- [ ] Admin reports

---

**Test Date:** ___________  
**Tester:** ___________  
**Result:** [ ] All Passed [ ] Partial Pass [ ] Failed