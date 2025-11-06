# Payment URL Fix Documentation

## Issue Description
The error `NoReverseMatch at /payments/initiate/3/ Reverse for 'detail' not found` occurs because the payments app is trying to use URL names that don't match the actual URL patterns defined in the orders app.

## Root Cause
In `payments/views.py`, the code references:
- `orders:detail` → but the actual URL name is `orders:order_detail`
- `orders:list` → but the actual URL name is `orders:order_list`

## Current Orders URL Patterns
From `orders/urls.py`:
```python
urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('', views.order_list, name='order_list'),  # ← This is 'order_list', not 'list'
    path('<int:order_id>/', views.order_detail, name='order_detail'),  # ← This is 'order_detail', not 'detail'
    path('<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),
]
```

## Required Fixes
All references in `payments/views.py` need to be updated:
1. `orders:detail` → `orders:order_detail`
2. `orders:list` → `orders:order_list`

## Status
✅ Fixed URL references in payments/views.py
- Lines 50, 70, 102, 178, 287 updated
- Both direct redirects and reverse URL generation in create_payment calls

## Testing
After the fix, the payment initiation URL should work correctly:
- `/payments/initiate/3/` should display the payment selection page
- Error handling should redirect to correct order detail pages
- Payment completion should redirect to correct order list page

## Note
This is NOT related to missing ECPay credentials. The payment system can display the payment selection page and handle the flow even without ECPay credentials configured. The actual payment processing will fail without credentials, but the URL routing should work.