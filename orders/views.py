"""
Order views for Taiwan e-commerce platform.
Handles order creation, checkout process, and order management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.urls import reverse
from django.db import transaction
from decimal import Decimal

from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    """
    Checkout page view - creates order from cart and redirects to payment.
    結帳頁面視圖 - 從購物車建立訂單並導向付款
    """
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, _('購物車是空的 / Your cart is empty'))
        return redirect('cart:cart')
    
    # Check if cart has items
    if not cart.items.exists():
        messages.error(request, _('購物車是空的 / Your cart is empty'))
        return redirect('cart:cart')
    
    # Check stock availability for all items
    unavailable_items = []
    for item in cart.items.all():
        if not item.is_available or not item.has_sufficient_stock:
            unavailable_items.append(item)
    
    if unavailable_items:
        messages.error(request, _('購物車中有商品缺貨或庫存不足 / Some items in your cart are out of stock'))
        return redirect('cart:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Create order from cart
            order = create_order_from_cart(cart, form.cleaned_data, request.user)
            
            if order:
                # Clear cart after successful order creation
                cart.clear()
                
                # Redirect to payment initiation
                return redirect('payments:initiate', order_id=order.id)
            else:
                messages.error(request, _('訂單建立失敗，請重試 / Order creation failed, please try again'))
    else:
        form = CheckoutForm(user=request.user)
    
    # Calculate totals
    subtotal = cart.get_subtotal()
    shipping_fee = calculate_shipping_fee(subtotal)
    total = subtotal + shipping_fee
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'form': form,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': total,
        'item_count': cart.get_items_count(),
    }
    
    return render(request, 'orders/checkout.html', context)


def create_order_from_cart(cart, form_data, user):
    """
    Create order from cart data.
    從購物車資料建立訂單
    """
    try:
        with transaction.atomic():
            # Calculate totals
            subtotal = cart.get_subtotal()
            shipping_fee = calculate_shipping_fee(subtotal)
            total = subtotal + shipping_fee
            
            # Create order
            order = Order.objects.create(
                user=user,
                status='pending',
                payment_status='pending',
                payment_method=form_data.get('payment_method', 'credit_card'),
                shipping_method=form_data.get('shipping_method', 'home_delivery'),
                recipient_name=form_data.get('recipient_name', ''),
                recipient_phone=form_data.get('recipient_phone', ''),
                shipping_postal_code=form_data.get('postal_code', ''),
                shipping_city=form_data.get('city', ''),
                shipping_district=form_data.get('district', ''),
                shipping_address=form_data.get('address', ''),
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                total_amount=total,
                customer_notes=form_data.get('notes', '')
            )
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku if hasattr(cart_item.product, 'sku') else '',
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.get_price()
                )
            
            return order
            
    except Exception as e:
        # Log error in production
        print(f"Order creation error: {str(e)}")
        return None


def calculate_shipping_fee(subtotal):
    """
    Calculate shipping fee based on subtotal.
    根據小計計算運費
    """
    # Taiwan shipping fee logic
    FREE_SHIPPING_THRESHOLD = Decimal('1500')  # NT$1,500 for free shipping
    STANDARD_SHIPPING_FEE = Decimal('60')      # NT$60 standard shipping
    
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal('0')
    return STANDARD_SHIPPING_FEE


def checkout_confirm(request):
    """
    Checkout confirmation - to be implemented
    結帳確認 - 待實作
    """
    return JsonResponse({
        'success': False,
        'message': _('功能開發中 / Feature under development')
    })


def checkout_success(request):
    """
    Checkout success page - to be implemented
    結帳成功頁面 - 待實作
    """
    return render(request, 'orders/checkout_success.html')


@login_required
def order_list(request):
    """
    User's order list.
    用戶訂單列表
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """
    Order detail view.
    訂單詳情視圖
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_invoice(request, order_id):
    """
    Order invoice view - to be implemented
    訂單發票視圖 - 待實作
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_invoice.html', context)
