from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.translation import gettext as _
from django.db.models import Sum, F
from products.models import Product, ProductVariant
from .models import Cart, CartItem
import json


def get_or_create_cart(request):
    """Get or create cart for user or guest session"""
    if request.user.is_authenticated:
        # For authenticated users, try to get existing cart, handle duplicates
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
        except Cart.MultipleObjectsReturned:
            # Handle duplicate carts - keep the first one, delete others
            carts = Cart.objects.filter(user=request.user).order_by('created_at')
            cart = carts.first()
            # Delete duplicates
            carts.exclude(id=cart.id).delete()
    else:
        # Use session for guest users
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        
        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(session_key=session_key)
        except Cart.MultipleObjectsReturned:
            # Handle duplicate session carts
            carts = Cart.objects.filter(session_key=session_key).order_by('created_at')
            cart = carts.first()
            # Merge items from duplicate carts and delete duplicates
            for duplicate_cart in carts.exclude(id=cart.id):
                for item in duplicate_cart.items.all():
                    item.cart = cart
                    item.save()
                duplicate_cart.delete()
    
    return cart


@require_POST
def add_to_cart(request):
    """Add product to cart (AJAX endpoint)"""
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            product_id = data.get('product_id')
            variant_id = data.get('variant_id')
            quantity = int(data.get('quantity', 1))
        else:
            # Handle form data
            product_id = request.POST.get('product_id')
            variant_id = request.POST.get('variant_id') 
            quantity = int(request.POST.get('quantity', 1))
        
        # Validate required fields
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': _('商品ID不能為空')
            }, status=400)
        
        # Validate product
        try:
            product = get_object_or_404(Product, id=product_id, status='active')
        except (ValueError, Product.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': _('商品不存在或無法購買')
            }, status=400)
        
        # Validate variant if provided
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
            if not variant.is_available:
                return JsonResponse({
                    'success': False,
                    'message': _('此規格目前缺貨')
                }, status=400)
        
        # Check stock
        available_stock = variant.stock if variant else product.stock
        if quantity > available_stock:
            return JsonResponse({
                'success': False,
                'message': _('庫存不足，目前剩餘 {} 件').format(available_stock)
            }, status=400)
        
        # Get or create cart
        cart = get_or_create_cart(request)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update existing cart item
            new_quantity = cart_item.quantity + quantity
            if new_quantity > available_stock:
                return JsonResponse({
                    'success': False,
                    'message': _('購物車數量已達庫存上限')
                }, status=400)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Calculate cart totals
        cart_total = cart.get_total()
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        
        return JsonResponse({
            'success': True,
            'message': _('已加入購物車'),
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'item_id': cart_item.id
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': _('商品不存在')
        }, status=404)
    except Exception as e:
        # Handle Http404 from get_object_or_404
        if 'No Product matches the given query' in str(e):
            return JsonResponse({
                'success': False,
                'message': _('商品不存在')
            }, status=404)
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': _('數量必須大於 0')
            }, status=400)
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock
        available_stock = cart_item.variant.stock if cart_item.variant else cart_item.product.stock
        if quantity > available_stock:
            return JsonResponse({
                'success': False,
                'message': _('庫存不足，目前剩餘 {} 件').format(available_stock)
            }, status=400)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Calculate totals
        item_subtotal = cart_item.get_total_price()
        cart_total = cart.get_total()
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        
        return JsonResponse({
            'success': True,
            'message': _('已更新數量'),
            'item_subtotal': float(item_subtotal),
            'cart_total': float(cart_total),
            'cart_count': cart_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        # Calculate new totals
        cart_total = cart.get_total()
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        
        return JsonResponse({
            'success': True,
            'message': _('已從購物車移除 {}').format(product_name),
            'cart_total': float(cart_total),
            'cart_count': cart_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def cart_view(request):
    """Display shopping cart"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'variant').order_by('-created_at')
    
    # Calculate totals
    subtotal = cart.get_subtotal()
    total = cart.get_total()
    item_count = cart_items.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Shipping fee calculation (example: free shipping over NT$1000)
    shipping_fee = 0 if subtotal >= 1000 else 60
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': total + shipping_fee,
        'item_count': item_count,
        'free_shipping_threshold': 1000,
        'shipping_remaining': max(0, 1000 - subtotal) if subtotal < 1000 else 0,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def clear_cart(request):
    """Clear all items from cart"""
    try:
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        
        messages.success(request, _('購物車已清空'))
        return JsonResponse({
            'success': True,
            'message': _('購物車已清空')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def get_cart_count(request):
    """Get cart item count (for AJAX updates)"""
    cart = get_or_create_cart(request)
    count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    return JsonResponse({'cart_count': count})
