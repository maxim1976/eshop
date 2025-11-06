"""
Orders admin interface - English Version.
Follows Django best practices and EShop coding standards.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, ShippingAddress


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price_at_purchase', 'subtotal_display')
    can_delete = False
    verbose_name = "Order Item"
    verbose_name_plural = "Order Items"
    
    def subtotal_display(self, obj):
        """Display item subtotal."""
        return format_html('NT$ {:,}', obj.get_subtotal())
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders."""
    
    list_display = (
        'order_number_display',
        'user_display',
        'status_display',
        'payment_status_display',
        'total_display',
        'payment_method_display',
        'shipping_method_display',
        'created_at'
    )
    list_filter = (
        'status',
        'payment_status',
        'payment_method',
        'shipping_method',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'order_number',
        'user__email',
        'recipient_name',
        'recipient_phone',
        'transaction_id'
    )
    readonly_fields = (
        'order_number',
        'created_at',
        'updated_at',
        'total_display',
        'items_summary'
    )
    date_hierarchy = 'created_at'
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'user',
                'status',
                'payment_status',
            )
        }),
        ('Amount Details (NT$)', {
            'fields': (
                'subtotal',
                'shipping_fee',
                'total_amount',
                'total_display',
            ),
            'description': 'Amounts in New Taiwan Dollar (NT$)'
        }),
        ('Payment Information', {
            'fields': (
                'payment_method',
                'transaction_id',
            )
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_method',
                'recipient_name',
                'recipient_phone',
                'shipping_postal_code',
                'shipping_city',
                'shipping_district',
                'shipping_address',
            )
        }),
        ('Notes', {
            'fields': (
                'customer_notes',
                'admin_notes',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
        ('Order Summary', {
            'fields': ('items_summary',),
            'classes': ('collapse',),
        }),
    )
    
    actions = [
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled'
    ]
    
    def order_number_display(self, obj):
        """Display order number with link."""
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="font-weight: bold; color: #2563eb;">📋 {}</a>',
            url,
            obj.order_number
        )
    order_number_display.short_description = 'Order Number'
    
    def user_display(self, obj):
        """Display user information."""
        if obj.user:
            return format_html(
                '<span style="color: #059669;">👤 {}</span>',
                obj.user.email
            )
        return format_html('<span style="color: #6b7280;">👥 Guest</span>')
    user_display.short_description = 'Customer'
    
    def status_display(self, obj):
        """Display order status with color coding."""
        status_colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'shipped': '#8b5cf6',
            'delivered': '#059669',
            'cancelled': '#dc2626',
            'refunded': '#6b7280',
        }
        status_labels = {
            'pending': 'Pending',
            'processing': 'Processing',
            'shipped': 'Shipped',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled',
            'refunded': 'Refunded',
        }
        color = status_colors.get(obj.status, '#6b7280')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            label
        )
    status_display.short_description = 'Status'
    
    def payment_status_display(self, obj):
        """Display payment status with color coding."""
        if obj.payment_status == 'paid':
            return format_html(
                '<span style="color: #059669; font-weight: bold;">✓ Paid</span>'
            )
        elif obj.payment_status == 'pending':
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">⏳ Pending</span>'
            )
        elif obj.payment_status == 'failed':
            return format_html(
                '<span style="color: #dc2626; font-weight: bold;">✗ Failed</span>'
            )
        else:  # refunded
            return format_html(
                '<span style="color: #6b7280; font-weight: bold;">↩ Refunded</span>'
            )
    payment_status_display.short_description = 'Payment'
    
    def total_display(self, obj):
        """Display total amount prominently."""
        return format_html(
            '<span style="font-size: 1.2em; font-weight: bold; color: #059669;">NT$ {:,}</span>',
            obj.total_amount
        )
    total_display.short_description = 'Total'
    
    def payment_method_display(self, obj):
        """Display payment method."""
        payment_labels = {
            'credit_card': 'Credit Card',
            'atm': 'ATM Transfer',
            'cvs_code': 'CVS Code',
            'line_pay': 'LINE Pay',
            'apple_pay': 'Apple Pay',
            'google_pay': 'Google Pay',
        }
        return payment_labels.get(obj.payment_method, obj.payment_method)
    payment_method_display.short_description = 'Payment Method'
    
    def shipping_method_display(self, obj):
        """Display shipping method."""
        shipping_labels = {
            'home_delivery': 'Home Delivery',
            'seven_eleven': '7-11 Pickup',
            'family_mart': 'FamilyMart Pickup',
            'hi_life': 'Hi-Life Pickup',
            'ok_mart': 'OK Mart Pickup',
        }
        return shipping_labels.get(obj.shipping_method, obj.shipping_method)
    shipping_method_display.short_description = 'Shipping'
    
    def items_summary(self, obj):
        """Display order items summary."""
        items = obj.items.all()
        if not items:
            return 'No items'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f3f4f6; font-weight: bold;">'
        html += '<th style="padding: 8px; text-align: left;">Product</th>'
        html += '<th style="padding: 8px; text-align: right;">Qty</th>'
        html += '<th style="padding: 8px; text-align: right;">Price</th>'
        html += '<th style="padding: 8px; text-align: right;">Subtotal</th>'
        html += '</tr>'
        
        for item in items:
            html += '<tr style="border-bottom: 1px solid #e5e7eb;">'
            html += f'<td style="padding: 8px;">{item.product.name_en}</td>'
            html += f'<td style="padding: 8px; text-align: right;">× {item.quantity}</td>'
            html += f'<td style="padding: 8px; text-align: right;">NT$ {item.price_at_purchase:,}</td>'
            html += f'<td style="padding: 8px; text-align: right; font-weight: bold;">NT$ {item.get_subtotal():,}</td>'
            html += '</tr>'
        
        html += '</table>'
        return mark_safe(html)
    items_summary.short_description = 'Order Details'
    
    # Bulk actions
    def mark_as_processing(self, request, queryset):
        """Set orders to processing status."""
        updated = queryset.update(status='processing')
        self.message_user(
            request,
            f'{updated} orders marked as processing'
        )
    mark_as_processing.short_description = 'Mark as Processing'
    
    def mark_as_shipped(self, request, queryset):
        """Set orders to shipped status."""
        updated = queryset.update(status='shipped')
        self.message_user(
            request,
            f'{updated} orders marked as shipped'
        )
    mark_as_shipped.short_description = 'Mark as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        """Set orders to delivered status."""
        updated = queryset.update(status='delivered')
        self.message_user(
            request,
            f'{updated} orders marked as delivered'
        )
    mark_as_delivered.short_description = 'Mark as Delivered'
    
    def mark_as_cancelled(self, request, queryset):
        """Set orders to cancelled status."""
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            f'{updated} orders cancelled'
        )
    mark_as_cancelled.short_description = 'Cancel Orders'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for order items."""
    
    list_display = (
        'order_display',
        'product',
        'variant_display',
        'quantity',
        'price_display',
        'subtotal_display'
    )
    list_filter = ('order__status', 'product__category')
    search_fields = ('order__order_number', 'product__name', 'product__name_en')
    readonly_fields = ('created_at', 'updated_at', 'price_at_purchase', 'subtotal_display')
    
    fieldsets = (
        ('Order Item', {
            'fields': (
                'order',
                'product',
                'variant',
                'quantity',
            )
        }),
        ('Pricing', {
            'fields': (
                'price_at_purchase',
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
    
    def order_display(self, obj):
        """Display order number."""
        return f"#{obj.order.order_number}"
    order_display.short_description = 'Order'
    
    def variant_display(self, obj):
        """Display variant if exists."""
        if obj.variant:
            return f"{obj.variant.name} / {obj.variant.name_en or obj.variant.name}"
        return '-'
    variant_display.short_description = 'Variant'
    
    def price_display(self, obj):
        """Display unit price."""
        return format_html('NT$ {:,}', obj.price_at_purchase)
    price_display.short_description = 'Price'
    
    def subtotal_display(self, obj):
        """Display subtotal."""
        return format_html(
            '<span style="font-weight: bold;">NT$ {:,}</span>',
            obj.get_subtotal()
        )
    subtotal_display.short_description = 'Subtotal'


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    """Admin interface for shipping addresses."""
    
    list_display = (
        'order_display',
        'recipient_name',
        'phone',
        'address_display',
        'created_at'
    )
    search_fields = (
        'order__order_number',
        'recipient_name',
        'phone',
        'city',
        'district',
        'address'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Recipient Information', {
            'fields': (
                'order',
                'recipient_name',
                'phone',
            )
        }),
        ('Address Information', {
            'fields': (
                'postal_code',
                'city',
                'district',
                'address',
            ),
            'description': 'Please use Taiwan address format'
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def order_display(self, obj):
        """Display order number."""
        return f"#{obj.order.order_number}"
    order_display.short_description = 'Order'
    
    def address_display(self, obj):
        """Display full Taiwan address."""
        return f"{obj.postal_code} {obj.city}{obj.district}{obj.address}"
    address_display.short_description = 'Full Address'