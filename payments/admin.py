"""
Admin configuration for payments app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Payment, PaymentLog, RefundRecord


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for Payment model.
    """
    
    list_display = [
        'payment_id',
        'order_link',
        'user_link',
        'payment_method',
        'status_badge',
        'amount_display',
        'ecpay_trade_no',
        'created_at',
        'paid_at',
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'currency',
        'created_at',
        'paid_at',
    ]
    
    search_fields = [
        'payment_id',
        'ecpay_merchant_trade_no',
        'ecpay_trade_no',
        'transaction_id',
        'order__order_number',
        'user__email',
    ]
    
    readonly_fields = [
        'payment_id',
        'ecpay_merchant_trade_no',
        'ecpay_trade_no',
        'ecpay_payment_date',
        'ecpay_payment_type',
        'ecpay_payment_type_charge_fee',
        'transaction_id',
        'auth_code',
        'created_at',
        'updated_at',
        'paid_at',
    ]
    
    fieldsets = [
        (_('基本資訊 / Basic Information'), {
            'fields': [
                'payment_id',
                'order',
                'user',
                'status',
                'payment_method',
            ]
        }),
        (_('金額資訊 / Amount Information'), {
            'fields': [
                'amount',
                'currency',
                'refund_amount',
                'refund_date',
            ]
        }),
        (_('ECPay 交易資訊 / ECPay Transaction Info'), {
            'fields': [
                'ecpay_merchant_trade_no',
                'ecpay_trade_no',
                'ecpay_payment_date',
                'ecpay_payment_type',
                'ecpay_payment_type_charge_fee',
            ]
        }),
        (_('付款詳細資訊 / Payment Details'), {
            'fields': [
                'transaction_id',
                'auth_code',
                'bank_code',
                'virtual_account',
                'payment_code',
                'barcode_1',
                'barcode_2',
                'barcode_3',
                'payment_deadline',
            ]
        }),
        (_('時間戳記 / Timestamps'), {
            'fields': [
                'created_at',
                'updated_at',
                'paid_at',
            ]
        }),
    ]
    
    def order_link(self, obj):
        """Create link to order admin."""
        if obj.order:
            return format_html(
                '<a href="/admin/orders/order/{}/change/">{}</a>',
                obj.order.id,
                obj.order.order_number
            )
        return '-'
    order_link.short_description = _('訂單 / Order')
    
    def user_link(self, obj):
        """Create link to user admin."""
        if obj.user:
            return format_html(
                '<a href="/admin/authentication/customuser/{}/change/">{}</a>',
                obj.user.id,
                obj.user.email
            )
        return '-'
    user_link.short_description = _('使用者 / User')
    
    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'paid': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'purple',
            'partial_refund': 'orange',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('狀態 / Status')
    
    def amount_display(self, obj):
        """Display amount with currency."""
        return f"NT$ {obj.amount:,.0f}"
    amount_display.short_description = _('金額 / Amount')


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    """
    Admin interface for PaymentLog model.
    """
    
    list_display = [
        'payment_link',
        'log_type_badge',
        'message_short',
        'ip_address',
        'created_at',
    ]
    
    list_filter = [
        'log_type',
        'created_at',
    ]
    
    search_fields = [
        'payment__payment_id',
        'message',
        'ip_address',
    ]
    
    readonly_fields = [
        'payment',
        'log_type',
        'message',
        'request_data',
        'response_data',
        'ip_address',
        'user_agent',
        'created_at',
    ]
    
    def payment_link(self, obj):
        """Create link to payment admin."""
        return format_html(
            '<a href="/admin/payments/payment/{}/change/">{}</a>',
            obj.payment.id,
            obj.payment.payment_id
        )
    payment_link.short_description = _('付款 / Payment')
    
    def log_type_badge(self, obj):
        """Display log type with color badge."""
        colors = {
            'request': 'blue',
            'response': 'green',
            'callback': 'orange',
            'error': 'red',
            'info': 'gray',
        }
        color = colors.get(obj.log_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_log_type_display()
        )
    log_type_badge.short_description = _('類型 / Type')
    
    def message_short(self, obj):
        """Display truncated message."""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = _('訊息 / Message')


@admin.register(RefundRecord)
class RefundRecordAdmin(admin.ModelAdmin):
    """
    Admin interface for RefundRecord model.
    """
    
    list_display = [
        'refund_id',
        'payment_link',
        'amount_display',
        'status_badge',
        'processed_by_link',
        'created_at',
        'processed_at',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'processed_at',
    ]
    
    search_fields = [
        'refund_id',
        'payment__payment_id',
        'ecpay_refund_no',
        'reason',
    ]
    
    readonly_fields = [
        'refund_id',
        'created_at',
        'processed_at',
    ]
    
    fieldsets = [
        (_('基本資訊 / Basic Information'), {
            'fields': [
                'refund_id',
                'payment',
                'amount',
                'reason',
                'status',
            ]
        }),
        (_('處理資訊 / Processing Information'), {
            'fields': [
                'ecpay_refund_no',
                'processed_by',
                'created_at',
                'processed_at',
            ]
        }),
    ]
    
    def payment_link(self, obj):
        """Create link to payment admin."""
        return format_html(
            '<a href="/admin/payments/payment/{}/change/">{}</a>',
            obj.payment.id,
            obj.payment.payment_id
        )
    payment_link.short_description = _('付款 / Payment')
    
    def processed_by_link(self, obj):
        """Create link to processed by user admin."""
        if obj.processed_by:
            return format_html(
                '<a href="/admin/authentication/customuser/{}/change/">{}</a>',
                obj.processed_by.id,
                obj.processed_by.email
            )
        return '-'
    processed_by_link.short_description = _('處理人 / Processed By')
    
    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('狀態 / Status')
    
    def amount_display(self, obj):
        """Display amount with currency."""
        return f"NT$ {obj.amount:,.0f}"
    amount_display.short_description = _('金額 / Amount')
