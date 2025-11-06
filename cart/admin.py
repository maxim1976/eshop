"""
Shopping cart admin interface - English Version.
Follows Django best practices and EShop coding standards.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price_at_addition', 'subtotal_display')
    can_delete = True
    verbose_name = "Cart Item"
    verbose_name_plural = "Cart Items"
    
    def subtotal_display(self, obj):
        """Display item subtotal."""
        try:
            total_price = obj.get_total_price()
            if total_price is not None:
                price = float(total_price)
                return format_html('NT$ {}', f"{price:,.0f}")
            else:
                return format_html('<span style="color: red;">計算錯誤 / Error</span>')
        except (TypeError, ValueError, AttributeError):
            return format_html('<span style="color: red;">計算錯誤 / Error</span>')
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for shopping carts."""
    
    list_display = (
        'cart_id_display',
        'user_display',
        'item_count',
        'total_display',
        'session_key_display',
        'created_at',
        'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'total_display', 'item_count_display')
    
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Cart Information', {
            'fields': (
                'user',
                'session_key',
            )
        }),
        ('Statistics', {
            'fields': (
                'item_count_display',
                'total_display',
                'created_at',
                'updated_at',
            )
        }),
    )
    
    def cart_id_display(self, obj):
        """Display cart ID."""
        return f"#{obj.id}"
    cart_id_display.short_description = 'Cart ID'
    
    def user_display(self, obj):
        """Display user or guest indicator."""
        if obj.user:
            return format_html(
                '<span style="color: #059669;">👤 {}</span>',
                obj.user.email
            )
        return format_html(
            '<span style="color: #6b7280;">👥 Guest</span>'
        )
    user_display.short_description = 'User'
    
    def session_key_display(self, obj):
        """Display session key (truncated for security)."""
        if obj.session_key:
            return f"{obj.session_key[:8]}..."
        return '-'
    session_key_display.short_description = 'Session Key'
    
    def item_count(self, obj):
        """Display number of items in cart."""
        count = obj.items.count()
        return format_html(
            '<span style="font-weight: bold;">{} items</span>',
            count
        )
    item_count.short_description = 'Item Count'
    
    def item_count_display(self, obj):
        """Display item count for detail view."""
        return f"{obj.items.count()} items"
    item_count_display.short_description = 'Items'
    
    def total_display(self, obj):
        """Display cart total."""
        try:
            total = obj.get_total()
            if total is not None:
                total_float = float(total)
                return format_html(
                    '<span style="font-size: 1.1em; font-weight: bold; color: #059669;">NT$ {}</span>',
                    f"{total_float:,.0f}"
                )
            else:
                return format_html('<span style="color: red;">計算錯誤 / Error</span>')
        except (TypeError, ValueError, AttributeError):
            return format_html('<span style="color: red;">計算錯誤 / Error</span>')
    total_display.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for cart items."""
    
    list_display = (
        'cart_display',
        'product',
        'variant_display',
        'quantity_display',
        'price_display',
        'subtotal_display',
        'created_at'
    )
    list_filter = ('created_at', 'product__category')
    search_fields = ('cart__user__email', 'product__name', 'product__name_en')
    readonly_fields = ('created_at', 'updated_at', 'price_at_addition', 'subtotal_display')
    
    fieldsets = (
        ('Cart Item', {
            'fields': (
                'cart',
                'product',
                'variant',
                'quantity',
            )
        }),
        ('Pricing', {
            'fields': (
                'price_at_addition',
                'subtotal_display',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    
    def cart_display(self, obj):
        """Display cart information."""
        if obj.cart.user:
            return format_html(
                '🛒 #{} ({})',
                obj.cart.id,
                obj.cart.user.email
            )
        return format_html('🛒 #{} (Guest)', obj.cart.id)
    cart_display.short_description = 'Cart'
    
    def variant_display(self, obj):
        """Display variant information."""
        if obj.variant:
            return f"{obj.variant.name} / {obj.variant.name_en or obj.variant.name}"
        return '-'
    variant_display.short_description = 'Variant'
    
    def quantity_display(self, obj):
        """Display quantity."""
        return format_html(
            '<span style="font-weight: bold;">× {}</span>',
            obj.quantity
        )
    quantity_display.short_description = 'Qty'
    
    def price_display(self, obj):
        """Display unit price."""
        try:
            price_at_addition = obj.price_at_addition
            if price_at_addition is not None:
                price = float(price_at_addition)
                return format_html('NT$ {}', f"{price:,.0f}")
            else:
                return format_html('<span style="color: red;">無價格 / No Price</span>')
        except (TypeError, ValueError, AttributeError):
            return format_html('<span style="color: red;">錯誤 / Error</span>')
    price_display.short_description = 'Unit Price'
    
    def subtotal_display(self, obj):
        """Display subtotal."""
        try:
            total_price = obj.get_total_price()
            if total_price is not None:
                price = float(total_price)
                return format_html(
                    '<span style="font-weight: bold; color: #059669;">NT$ {}</span>',
                    f"{price:,.0f}"
                )
            else:
                return format_html('<span style="color: red;">計算錯誤 / Error</span>')
        except (TypeError, ValueError, AttributeError):
            return format_html('<span style="color: red;">計算錯誤 / Error</span>')
    subtotal_display.short_description = 'Subtotal'