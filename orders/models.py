"""
Order models for Taiwan e-commerce platform.
Handles orders, order items, and shipping addresses with Taiwan-specific features.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from products.models import Product, ProductVariant
import uuid

User = get_user_model()


class Order(models.Model):
    """
    Order model with Taiwan-specific payment and shipping methods.
    Follows PDPA compliance for Taiwan market.
    """
    
    # Order Status Choices
    STATUS_CHOICES = [
        ('pending', _('待處理 / Pending')),
        ('processing', _('處理中 / Processing')),
        ('shipped', _('已出貨 / Shipped')),
        ('delivered', _('已送達 / Delivered')),
        ('cancelled', _('已取消 / Cancelled')),
        ('refunded', _('已退款 / Refunded')),
    ]
    
    # Payment Status Choices
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('待付款 / Pending')),
        ('paid', _('已付款 / Paid')),
        ('failed', _('付款失敗 / Failed')),
        ('refunded', _('已退款 / Refunded')),
    ]
    
    # Taiwan-specific Payment Methods
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', _('信用卡 / Credit Card')),
        ('atm', _('ATM 轉帳 / ATM Transfer')),
        ('cvs_code', _('超商代碼 / CVS Code')),
        ('line_pay', 'LINE Pay'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]
    
    # Taiwan-specific Shipping Methods
    SHIPPING_METHOD_CHOICES = [
        ('home_delivery', _('宅配 / Home Delivery')),
        ('seven_eleven', _('7-11 取貨 / 7-11 Pickup')),
        ('family_mart', _('全家取貨 / FamilyMart Pickup')),
        ('hi_life', _('萊爾富取貨 / Hi-Life Pickup')),
        ('ok_mart', _('OK超商取貨 / OK Mart Pickup')),
    ]
    
    # Order Identification
    order_number = models.CharField(
        _('訂單編號 / Order Number'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('系統自動生成 / Auto-generated')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('使用者 / User')
    )
    
    # Order Status
    status = models.CharField(
        _('訂單狀態 / Order Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    payment_status = models.CharField(
        _('付款狀態 / Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Payment Information
    payment_method = models.CharField(
        _('付款方式 / Payment Method'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        default='credit_card'
    )
    
    transaction_id = models.CharField(
        _('交易編號 / Transaction ID'),
        max_length=100,
        blank=True,
        null=True
    )
    
    # Shipping Information
    shipping_method = models.CharField(
        _('配送方式 / Shipping Method'),
        max_length=20,
        choices=SHIPPING_METHOD_CHOICES,
        blank=True,
        default='home_delivery'
    )
    
    # Recipient Information (Taiwan format)
    recipient_name = models.CharField(
        _('收件人姓名 / Recipient Name'),
        max_length=100,
        blank=True,
        default=''
    )
    
    recipient_phone = models.CharField(
        _('收件人電話 / Recipient Phone'),
        max_length=20,
        blank=True,
        default=''
    )
    
    # Taiwan Address Format
    shipping_postal_code = models.CharField(
        _('郵遞區號 / Postal Code'),
        max_length=10,
        blank=True,
        default=''
    )
    
    shipping_city = models.CharField(
        _('縣市 / City'),
        max_length=50,
        blank=True,
        default=''
    )
    
    shipping_district = models.CharField(
        _('區域 / District'),
        max_length=50,
        blank=True,
        default=''
    )
    
    shipping_address = models.CharField(
        _('詳細地址 / Detailed Address'),
        max_length=255,
        blank=True,
        default=''
    )
    
    # Order Amounts (in NT$)
    subtotal = models.DecimalField(
        _('商品小計 / Subtotal'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    shipping_fee = models.DecimalField(
        _('運費 / Shipping Fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    total_amount = models.DecimalField(
        _('總金額 / Total Amount'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Notes
    customer_notes = models.TextField(
        _('客戶備註 / Customer Notes'),
        blank=True
    )
    
    admin_notes = models.TextField(
        _('管理員備註 / Admin Notes'),
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('建立時間 / Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('訂單 / Order')
        verbose_name_plural = _('訂單 / Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.user.email if self.user else 'Guest'}"
    
    def save(self, *args, **kwargs):
        """Generate order number if not exists."""
        if not self.order_number:
            # Format: ES-YYYYMMDD-XXXXX (ES = EShop)
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4().hex)[:5].upper()
            self.order_number = f"ES-{timestamp}-{random_suffix}"
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """Return full Taiwan-formatted address."""
        if not self.shipping_address:
            return _('未提供地址 / No address provided')
        return f"{self.shipping_postal_code} {self.shipping_city}{self.shipping_district}{self.shipping_address}"


class OrderItem(models.Model):
    """
    Individual items within an order.
    Stores product information at time of purchase.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('訂單 / Order')
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('商品 / Product')
    )
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('規格 / Variant')
    )
    
    # Product information at time of purchase (for historical records)
    product_name = models.CharField(
        _('商品名稱 / Product Name'),
        max_length=255,
        blank=True,
        default=''
    )
    
    product_sku = models.CharField(
        _('商品編號 / SKU'),
        max_length=100,
        blank=True,
        default=''
    )
    
    # Quantity and pricing
    quantity = models.PositiveIntegerField(
        _('數量 / Quantity'),
        default=1
    )
    
    price_at_purchase = models.DecimalField(
        _('購買時價格 / Price at Purchase'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('新台幣 (NT$) / New Taiwan Dollar')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('建立時間 / Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('訂單項目 / Order Item')
        verbose_name_plural = _('訂單項目 / Order Items')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name or self.product.name if self.product else 'Unknown'} x {self.quantity}"
    
    def get_subtotal(self):
        """Calculate line item subtotal."""
        return self.price_at_purchase * self.quantity


class ShippingAddress(models.Model):
    """
    Historical shipping addresses for orders.
    Separate model for data integrity and PDPA compliance.
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='shipping_address_detail',
        verbose_name=_('訂單 / Order')
    )
    
    # Recipient Information
    recipient_name = models.CharField(
        _('收件人姓名 / Recipient Name'),
        max_length=100,
        blank=True,
        default=''
    )
    
    phone = models.CharField(
        _('電話 / Phone'),
        max_length=20,
        blank=True,
        default=''
    )
    
    # Taiwan Address Format
    postal_code = models.CharField(
        _('郵遞區號 / Postal Code'),
        max_length=10,
        blank=True,
        default=''
    )
    
    city = models.CharField(
        _('縣市 / City'),
        max_length=50,
        blank=True,
        default=''
    )
    
    district = models.CharField(
        _('區域 / District'),
        max_length=50,
        blank=True,
        default=''
    )
    
    address = models.CharField(
        _('詳細地址 / Detailed Address'),
        max_length=255,
        blank=True,
        default=''
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('建立時間 / Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('配送地址 / Shipping Address')
        verbose_name_plural = _('配送地址 / Shipping Addresses')
    
    def __str__(self):
        return f"{self.recipient_name or 'Unknown'} - {self.get_full_address()}"
    
    def get_full_address(self):
        """Return full Taiwan-formatted address."""
        if not self.address:
            return _('未提供地址 / No address provided')
        return f"{self.postal_code} {self.city}{self.district}{self.address}"
