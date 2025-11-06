"""
Payment models for Taiwan e-commerce platform with ECPay integration.
Handles payment records, transaction logs, and ECPay-specific data.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from orders.models import Order

User = get_user_model()


class Payment(models.Model):
    """
    Main payment record with ECPay integration.
    Stores payment information and transaction status.
    """
    
    # ECPay Payment Method Choices
    PAYMENT_METHOD_CHOICES = [
        ('Credit', _('信用卡 / Credit Card')),
        ('WebATM', _('網路ATM / Web ATM')),
        ('ATM', _('ATM轉帳 / ATM Transfer')),
        ('CVS', _('超商代碼 / CVS Code Payment')),
        ('BARCODE', _('超商條碼 / CVS Barcode Payment')),
        ('AndroidPay', 'Android Pay'),
        ('ApplePay', 'Apple Pay'),
        ('LinePay', 'LINE Pay'),
    ]
    
    # Payment Status Choices
    STATUS_CHOICES = [
        ('pending', _('待付款 / Pending')),
        ('processing', _('處理中 / Processing')),
        ('paid', _('已付款 / Paid')),
        ('failed', _('付款失敗 / Failed')),
        ('cancelled', _('已取消 / Cancelled')),
        ('refunded', _('已退款 / Refunded')),
        ('partial_refund', _('部分退款 / Partial Refund')),
    ]
    
    # Payment Identification
    payment_id = models.CharField(
        _('付款編號 / Payment ID'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('系統自動生成 / Auto-generated')
    )
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name=_('訂單 / Order')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('使用者 / User')
    )
    
    # Payment Information
    payment_method = models.CharField(
        _('付款方式 / Payment Method'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='Credit'
    )
    
    status = models.CharField(
        _('付款狀態 / Payment Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Amount Information (in NT$)
    amount = models.DecimalField(
        _('付款金額 / Payment Amount'),
        max_digits=10,
        decimal_places=2,
        help_text=_('新台幣 (NT$) / New Taiwan Dollar')
    )
    
    currency = models.CharField(
        _('貨幣 / Currency'),
        max_length=3,
        default='TWD',
        help_text=_('貨幣代碼 / Currency Code')
    )
    
    # ECPay Transaction Information
    ecpay_merchant_trade_no = models.CharField(
        _('ECPay商店交易編號 / ECPay Merchant Trade No'),
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    
    ecpay_trade_no = models.CharField(
        _('ECPay交易編號 / ECPay Trade No'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('ECPay系統交易編號 / ECPay system transaction number')
    )
    
    ecpay_payment_date = models.DateTimeField(
        _('ECPay付款時間 / ECPay Payment Date'),
        null=True,
        blank=True
    )
    
    ecpay_payment_type = models.CharField(
        _('ECPay付款類型 / ECPay Payment Type'),
        max_length=50,
        blank=True,
        help_text=_('ECPay回傳的付款類型 / Payment type returned by ECPay')
    )
    
    ecpay_payment_type_charge_fee = models.DecimalField(
        _('ECPay手續費 / ECPay Charge Fee'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('ECPay收取的手續費 / Fee charged by ECPay')
    )
    
    # Transaction Information
    transaction_id = models.CharField(
        _('交易編號 / Transaction ID'),
        max_length=100,
        blank=True,
        help_text=_('銀行或第三方支付交易編號 / Bank or third-party transaction ID')
    )
    
    auth_code = models.CharField(
        _('授權碼 / Authorization Code'),
        max_length=50,
        blank=True,
        help_text=_('信用卡授權碼 / Credit card authorization code')
    )
    
    # Payment Details for specific methods
    bank_code = models.CharField(
        _('銀行代碼 / Bank Code'),
        max_length=10,
        blank=True,
        help_text=_('ATM轉帳銀行代碼 / ATM transfer bank code')
    )
    
    virtual_account = models.CharField(
        _('虛擬帳號 / Virtual Account'),
        max_length=20,
        blank=True,
        help_text=_('ATM轉帳虛擬帳號 / ATM transfer virtual account')
    )
    
    payment_code = models.CharField(
        _('繳費代碼 / Payment Code'),
        max_length=20,
        blank=True,
        help_text=_('超商繳費代碼 / CVS payment code')
    )
    
    barcode_1 = models.CharField(
        _('條碼1 / Barcode 1'),
        max_length=20,
        blank=True
    )
    
    barcode_2 = models.CharField(
        _('條碼2 / Barcode 2'),
        max_length=20,
        blank=True
    )
    
    barcode_3 = models.CharField(
        _('條碼3 / Barcode 3'),
        max_length=20,
        blank=True
    )
    
    # Payment deadline for ATM/CVS
    payment_deadline = models.DateTimeField(
        _('付款期限 / Payment Deadline'),
        null=True,
        blank=True,
        help_text=_('ATM或超商付款期限 / ATM or CVS payment deadline')
    )
    
    # Refund Information
    refund_amount = models.DecimalField(
        _('退款金額 / Refund Amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    refund_date = models.DateTimeField(
        _('退款日期 / Refund Date'),
        null=True,
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
    
    paid_at = models.DateTimeField(
        _('付款完成時間 / Paid At'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('付款記錄 / Payment')
        verbose_name_plural = _('付款記錄 / Payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['payment_id']),
            models.Index(fields=['ecpay_merchant_trade_no']),
            models.Index(fields=['ecpay_trade_no']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.payment_id} - {self.order.order_number} - NT${self.amount}"
    
    def save(self, *args, **kwargs):
        """Generate payment ID if not exists."""
        if not self.payment_id:
            # Format: PAY-YYYYMMDD-XXXXX
            timestamp = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4().hex)[:5].upper()
            self.payment_id = f"PAY-{timestamp}-{random_suffix}"
        
        # Generate ECPay merchant trade no if not exists
        if not self.ecpay_merchant_trade_no:
            # ECPay requires max 20 characters, alphanumeric only
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_suffix = str(uuid.uuid4().hex)[:2].upper()
            self.ecpay_merchant_trade_no = f"ES{timestamp}{random_suffix}"
        
        super().save(*args, **kwargs)
    
    def mark_as_paid(self, transaction_data=None):
        """Mark payment as paid and update related information."""
        self.status = 'paid'
        self.paid_at = timezone.now()
        
        if transaction_data:
            self.ecpay_trade_no = transaction_data.get('TradeNo', '')
            self.ecpay_payment_date = timezone.now()
            self.ecpay_payment_type = transaction_data.get('PaymentType', '')
            self.transaction_id = transaction_data.get('gwsr', '')
            self.auth_code = transaction_data.get('auth_code', '')
        
        # Update order payment status
        self.order.payment_status = 'paid'
        self.order.save(update_fields=['payment_status'])
        
        self.save()
    
    def mark_as_failed(self, reason=''):
        """Mark payment as failed."""
        self.status = 'failed'
        
        # Update order payment status
        self.order.payment_status = 'failed'
        self.order.save(update_fields=['payment_status'])
        
        self.save()
    
    def can_refund(self):
        """Check if payment can be refunded."""
        return (
            self.status == 'paid' and 
            self.refund_amount < self.amount
        )
    
    def get_remaining_refundable_amount(self):
        """Get remaining amount that can be refunded."""
        return self.amount - self.refund_amount


class PaymentLog(models.Model):
    """
    Detailed logs of payment transactions and ECPay communications.
    Used for debugging and audit trail.
    """
    
    LOG_TYPE_CHOICES = [
        ('request', _('請求 / Request')),
        ('response', _('回應 / Response')),
        ('callback', _('回調 / Callback')),
        ('error', _('錯誤 / Error')),
        ('info', _('資訊 / Info')),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('付款記錄 / Payment')
    )
    
    log_type = models.CharField(
        _('日誌類型 / Log Type'),
        max_length=20,
        choices=LOG_TYPE_CHOICES,
        default='info'
    )
    
    message = models.TextField(
        _('訊息 / Message'),
        help_text=_('日誌訊息內容 / Log message content')
    )
    
    request_data = models.JSONField(
        _('請求資料 / Request Data'),
        null=True,
        blank=True,
        help_text=_('發送給ECPay的資料 / Data sent to ECPay')
    )
    
    response_data = models.JSONField(
        _('回應資料 / Response Data'),
        null=True,
        blank=True,
        help_text=_('ECPay回傳的資料 / Data returned from ECPay')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP地址 / IP Address'),
        null=True,
        blank=True,
        help_text=_('發起請求的IP地址 / IP address of the request')
    )
    
    user_agent = models.TextField(
        _('用戶代理 / User Agent'),
        blank=True,
        help_text=_('瀏覽器用戶代理字符串 / Browser user agent string')
    )
    
    created_at = models.DateTimeField(
        _('建立時間 / Created At'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('付款日誌 / Payment Log')
        verbose_name_plural = _('付款日誌 / Payment Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', '-created_at']),
            models.Index(fields=['log_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.payment.payment_id} - {self.log_type} - {self.created_at}"


class RefundRecord(models.Model):
    """
    Records of refund transactions.
    """
    
    REFUND_STATUS_CHOICES = [
        ('pending', _('待處理 / Pending')),
        ('processing', _('處理中 / Processing')),
        ('completed', _('已完成 / Completed')),
        ('failed', _('失敗 / Failed')),
        ('cancelled', _('已取消 / Cancelled')),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name=_('付款記錄 / Payment')
    )
    
    refund_id = models.CharField(
        _('退款編號 / Refund ID'),
        max_length=50,
        unique=True,
        editable=False
    )
    
    amount = models.DecimalField(
        _('退款金額 / Refund Amount'),
        max_digits=10,
        decimal_places=2,
        help_text=_('新台幣 (NT$) / New Taiwan Dollar')
    )
    
    reason = models.TextField(
        _('退款原因 / Refund Reason'),
        help_text=_('退款申請原因 / Reason for refund request')
    )
    
    status = models.CharField(
        _('退款狀態 / Refund Status'),
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='pending'
    )
    
    ecpay_refund_no = models.CharField(
        _('ECPay退款編號 / ECPay Refund No'),
        max_length=50,
        blank=True,
        help_text=_('ECPay系統退款編號 / ECPay system refund number')
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds',
        verbose_name=_('處理人 / Processed By')
    )
    
    created_at = models.DateTimeField(
        _('建立時間 / Created At'),
        auto_now_add=True
    )
    
    processed_at = models.DateTimeField(
        _('處理時間 / Processed At'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('退款記錄 / Refund Record')
        verbose_name_plural = _('退款記錄 / Refund Records')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.refund_id} - NT${self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Generate refund ID if not exists."""
        if not self.refund_id:
            # Format: REF-YYYYMMDD-XXXXX
            timestamp = timezone.now().strftime('%Y%m%d')
            random_suffix = str(uuid.uuid4().hex)[:5].upper()
            self.refund_id = f"REF-{timestamp}-{random_suffix}"
        
        super().save(*args, **kwargs)
