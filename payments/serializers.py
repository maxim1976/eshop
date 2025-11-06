"""
Serializers for payment API endpoints.
"""

from rest_framework import serializers
from .models import Payment, PaymentLog, RefundRecord


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model with localized fields.
    """
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'payment_id',
            'order_number',
            'user_email',
            'payment_method',
            'payment_method_display',
            'status',
            'status_display',
            'amount',
            'currency',
            'ecpay_merchant_trade_no',
            'ecpay_trade_no',
            'ecpay_payment_date',
            'ecpay_payment_type',
            'transaction_id',
            'auth_code',
            'bank_code',
            'virtual_account',
            'payment_code',
            'barcode_1',
            'barcode_2',
            'barcode_3',
            'payment_deadline',
            'refund_amount',
            'refund_date',
            'created_at',
            'updated_at',
            'paid_at',
        ]
        read_only_fields = [
            'payment_id',
            'ecpay_merchant_trade_no',
            'ecpay_trade_no',
            'ecpay_payment_date',
            'ecpay_payment_type',
            'transaction_id',
            'auth_code',
            'bank_code',
            'virtual_account',
            'payment_code',
            'barcode_1',
            'barcode_2',
            'barcode_3',
            'payment_deadline',
            'refund_amount',
            'refund_date',
            'created_at',
            'updated_at',
            'paid_at',
        ]


class PaymentLogSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentLog model.
    """
    
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    log_type_display = serializers.CharField(source='get_log_type_display', read_only=True)
    
    class Meta:
        model = PaymentLog
        fields = [
            'id',
            'payment_id',
            'log_type',
            'log_type_display',
            'message',
            'request_data',
            'response_data',
            'ip_address',
            'user_agent',
            'created_at',
        ]
        read_only_fields = '__all__'


class RefundRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for RefundRecord model.
    """
    
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_by_email = serializers.CharField(source='processed_by.email', read_only=True)
    
    class Meta:
        model = RefundRecord
        fields = [
            'refund_id',
            'payment_id',
            'amount',
            'reason',
            'status',
            'status_display',
            'ecpay_refund_no',
            'processed_by_email',
            'created_at',
            'processed_at',
        ]
        read_only_fields = [
            'refund_id',
            'ecpay_refund_no',
            'processed_by_email',
            'created_at',
            'processed_at',
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """
    Serializer for payment creation API.
    """
    
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        default='Credit'
    )
    client_back_url = serializers.URLField(required=False, allow_blank=True)
    order_result_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to user."""
        from orders.models import Order
        
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        try:
            order = Order.objects.get(id=value, user=request.user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        
        if order.payment_status != 'pending':
            raise serializers.ValidationError("Order cannot be paid")
        
        if hasattr(order, 'payment'):
            raise serializers.ValidationError("Payment already exists for this order")
        
        return value


class PaymentStatusQuerySerializer(serializers.Serializer):
    """
    Serializer for payment status query.
    """
    
    payment_id = serializers.CharField()
    
    def validate_payment_id(self, value):
        """Validate that payment exists and belongs to user."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        try:
            payment = Payment.objects.get(payment_id=value, user=request.user)
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found")
        
        return value