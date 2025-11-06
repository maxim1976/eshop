"""
ECPay payment service for Taiwan e-commerce platform.
Handles ECPay API integration, payment processing, and callback verification.
"""

import hashlib
import urllib.parse
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional
import requests
import logging
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

logger = logging.getLogger(__name__)


class ECPayService:
    """
    ECPay payment gateway integration service.
    Handles payment creation, callback verification, and refunds.
    """
    
    # ECPay API URLs
    SANDBOX_HOST = 'https://payment-stage.ecpay.com.tw'
    PRODUCTION_HOST = 'https://payment.ecpay.com.tw'
    
    # API Endpoints
    CREATE_PAYMENT_ENDPOINT = '/Cashier/AioCheckOut/V5'
    QUERY_TRADE_ENDPOINT = '/Cashier/QueryTradeInfo/V5'
    REFUND_ENDPOINT = '/CreditDetail/DoAction'
    
    def __init__(self):
        """Initialize ECPay service with settings."""
        self.merchant_id = getattr(settings, 'ECPAY_MERCHANT_ID', '')
        self.hash_key = getattr(settings, 'ECPAY_HASH_KEY', '')
        self.hash_iv = getattr(settings, 'ECPAY_HASH_IV', '')
        self.sandbox = getattr(settings, 'ECPAY_SANDBOX', True)
        
        self.host = self.SANDBOX_HOST if self.sandbox else self.PRODUCTION_HOST
        
        if not all([self.merchant_id, self.hash_key, self.hash_iv]):
            raise ValueError("ECPay credentials not properly configured")
    
    def generate_check_mac_value(self, parameters: Dict[str, Any]) -> str:
        """
        Generate CheckMacValue for ECPay API requests.
        This is ECPay's security mechanism to verify request integrity.
        """
        # Remove CheckMacValue if exists
        params = {k: v for k, v in parameters.items() if k != 'CheckMacValue'}
        
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Add HashKey and HashIV
        raw_string = f"HashKey={self.hash_key}&{query_string}&HashIV={self.hash_iv}"
        
        # URL encode
        encoded_string = urllib.parse.quote_plus(raw_string, safe='')
        
        # Convert to lowercase
        encoded_string = encoded_string.lower()
        
        # Generate SHA256 hash
        hash_value = hashlib.sha256(encoded_string.encode('utf-8')).hexdigest()
        
        # Convert to uppercase
        return hash_value.upper()
    
    def verify_callback_mac(self, callback_data: Dict[str, Any]) -> bool:
        """
        Verify the CheckMacValue from ECPay callback to ensure data integrity.
        """
        if 'CheckMacValue' not in callback_data:
            return False
        
        received_mac = callback_data['CheckMacValue']
        calculated_mac = self.generate_check_mac_value(callback_data)
        
        return received_mac == calculated_mac
    
    def create_payment_form_data(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create form data for ECPay payment request.
        Returns dictionary with all required ECPay parameters.
        """
        # Required parameters
        form_data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': payment_data['merchant_trade_no'],
            'MerchantTradeDate': payment_data['trade_date'].strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': 'aio',
            'TotalAmount': int(payment_data['amount']),
            'TradeDesc': payment_data.get('description', '商品購買'),
            'ItemName': payment_data.get('item_name', '商品'),
            'ReturnURL': payment_data['return_url'],
            'ChoosePayment': payment_data.get('payment_method', 'Credit'),
            'ClientBackURL': payment_data.get('client_back_url', ''),
            'ItemURL': payment_data.get('item_url', ''),
            'Remark': payment_data.get('remark', ''),
            'ChooseSubPayment': payment_data.get('sub_payment_method', ''),
            'OrderResultURL': payment_data.get('order_result_url', ''),
            'NeedExtraPaidInfo': 'Y',
            'DeviceSource': payment_data.get('device_source', ''),
            'IgnorePayment': payment_data.get('ignore_payment', ''),
            'PlatformID': payment_data.get('platform_id', ''),
            'InvoiceMark': 'N',  # 不開發票
            'CustomField1': payment_data.get('custom_field_1', ''),
            'CustomField2': payment_data.get('custom_field_2', ''),
            'CustomField3': payment_data.get('custom_field_3', ''),
            'CustomField4': payment_data.get('custom_field_4', ''),
        }
        
        # Remove empty values
        form_data = {k: v for k, v in form_data.items() if v}
        
        # Generate CheckMacValue
        check_mac_value = self.generate_check_mac_value(form_data)
        form_data['CheckMacValue'] = check_mac_value
        
        return form_data
    
    def get_payment_url(self) -> str:
        """Get ECPay payment URL based on environment."""
        return f"{self.host}{self.CREATE_PAYMENT_ENDPOINT}"
    
    def query_trade_info(self, merchant_trade_no: str) -> Optional[Dict[str, Any]]:
        """
        Query trade information from ECPay.
        Used to check payment status.
        """
        query_data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': merchant_trade_no,
            'TimeStamp': int(datetime.now().timestamp()),
        }
        
        # Generate CheckMacValue
        check_mac_value = self.generate_check_mac_value(query_data)
        query_data['CheckMacValue'] = check_mac_value
        
        try:
            response = requests.post(
                f"{self.host}{self.QUERY_TRADE_ENDPOINT}",
                data=query_data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse response (ECPay returns URL-encoded string)
                result = dict(urllib.parse.parse_qsl(response.text))
                return result
            else:
                logger.error(f"ECPay query failed: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"ECPay query request failed: {str(e)}")
            return None
    
    def process_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ECPay payment callback and return normalized result.
        """
        # Verify MAC first
        if not self.verify_callback_mac(callback_data):
            logger.error("ECPay callback MAC verification failed")
            return {
                'success': False,
                'error': 'MAC verification failed',
                'rtn_code': callback_data.get('RtnCode', ''),
                'rtn_msg': callback_data.get('RtnMsg', '')
            }
        
        # Check payment result
        rtn_code = callback_data.get('RtnCode', '')
        trade_status = callback_data.get('TradeStatus', '')
        
        success = rtn_code == '1' and trade_status == '1'
        
        result = {
            'success': success,
            'merchant_trade_no': callback_data.get('MerchantTradeNo', ''),
            'trade_no': callback_data.get('TradeNo', ''),
            'rtn_code': rtn_code,
            'rtn_msg': callback_data.get('RtnMsg', ''),
            'trade_date': callback_data.get('TradeDate', ''),
            'payment_type': callback_data.get('PaymentType', ''),
            'payment_type_charge_fee': callback_data.get('PaymentTypeChargeFee', '0'),
            'trade_amt': callback_data.get('TradeAmt', '0'),
            'auth_code': callback_data.get('auth_code', ''),
            'gwsr': callback_data.get('gwsr', ''),
            'process_date': callback_data.get('process_date', ''),
            'bank_code': callback_data.get('BankCode', ''),
            'v_account': callback_data.get('vAccount', ''),
            'exp_date': callback_data.get('ExpDate', ''),
            'payment_no': callback_data.get('PaymentNo', ''),
            'barcode_1': callback_data.get('Barcode1', ''),
            'barcode_2': callback_data.get('Barcode2', ''),
            'barcode_3': callback_data.get('Barcode3', ''),
        }
        
        return result
    
    def create_refund_request(self, refund_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create refund request to ECPay.
        Note: Refunds may require manual approval in ECPay backend.
        """
        # ECPay refund parameters
        refund_request = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': refund_data['merchant_trade_no'],
            'TradeNo': refund_data['trade_no'],
            'Action': 'R',  # R for refund
            'TotalAmount': int(refund_data['amount']),
            'TimeStamp': int(datetime.now().timestamp()),
        }
        
        # Generate CheckMacValue
        check_mac_value = self.generate_check_mac_value(refund_request)
        refund_request['CheckMacValue'] = check_mac_value
        
        try:
            response = requests.post(
                f"{self.host}{self.REFUND_ENDPOINT}",
                data=refund_request,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse response
                result = dict(urllib.parse.parse_qsl(response.text))
                return result
            else:
                logger.error(f"ECPay refund request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"ECPay refund request failed: {str(e)}")
            return None
    
    def get_payment_methods_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Get payment methods configuration for frontend.
        """
        return {
            'Credit': {
                'name': '信用卡 / Credit Card',
                'name_en': 'Credit Card',
                'name_zh': '信用卡',
                'description': '支援 Visa、MasterCard、JCB',
                'icon': 'credit-card',
                'processing_time': '即時',
                'fee_description': '不收取額外手續費'
            },
            'WebATM': {
                'name': '網路ATM / Web ATM',
                'name_en': 'Web ATM',
                'name_zh': '網路ATM',
                'description': '使用讀卡機進行轉帳',
                'icon': 'university',
                'processing_time': '即時',
                'fee_description': '依各銀行收費標準'
            },
            'ATM': {
                'name': 'ATM轉帳 / ATM Transfer',
                'name_en': 'ATM Transfer',
                'name_zh': 'ATM轉帳',
                'description': '至ATM機器或網銀轉帳',
                'icon': 'university',
                'processing_time': '3個工作天內',
                'fee_description': '依各銀行收費標準'
            },
            'CVS': {
                'name': '超商代碼 / CVS Code',
                'name_en': 'CVS Code Payment',
                'name_zh': '超商代碼',
                'description': '7-11、全家、萊爾富、OK超商',
                'icon': 'store',
                'processing_time': '即時',
                'fee_description': 'NT$30 服務費'
            },
            'BARCODE': {
                'name': '超商條碼 / CVS Barcode',
                'name_en': 'CVS Barcode Payment',
                'name_zh': '超商條碼',
                'description': '7-11、全家、萊爾富、OK超商',
                'icon': 'barcode',
                'processing_time': '即時',
                'fee_description': 'NT$30 服務費'
            },
        }


class PaymentService:
    """
    High-level payment service that coordinates with ECPay and manages payment records.
    """
    
    def __init__(self):
        self.ecpay = ECPayService()
    
    def create_payment(self, order, payment_method='Credit', **kwargs) -> Dict[str, Any]:
        """
        Create a new payment for an order.
        Returns payment form data for frontend submission.
        """
        from .models import Payment, PaymentLog
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=order.user,
            payment_method=payment_method,
            amount=order.total_amount,
            currency='TWD'
        )
        
        # Prepare ECPay payment data
        payment_data = {
            'merchant_trade_no': payment.ecpay_merchant_trade_no,
            'trade_date': timezone.now(),
            'amount': payment.amount,
            'description': f"訂單 {order.order_number}",
            'item_name': self._get_order_items_name(order),
            'return_url': self._build_return_url(),
            'client_back_url': kwargs.get('client_back_url', ''),
            'payment_method': payment_method,
            'order_result_url': kwargs.get('order_result_url', ''),
        }
        
        # Create ECPay form data
        form_data = self.ecpay.create_payment_form_data(payment_data)
        
        # Log the payment creation
        PaymentLog.objects.create(
            payment=payment,
            log_type='request',
            message='Payment created and ECPay form data generated',
            request_data=form_data,
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent', '')
        )
        
        return {
            'success': True,
            'payment': payment,
            'form_data': form_data,
            'action_url': self.ecpay.get_payment_url(),
            'method': 'POST'
        }
    
    def handle_callback(self, callback_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Handle ECPay payment callback.
        Updates payment status and order status.
        """
        from .models import Payment, PaymentLog
        
        # Process callback with ECPay service
        result = self.ecpay.process_callback(callback_data)
        
        # Find payment record
        merchant_trade_no = result.get('merchant_trade_no', '')
        try:
            payment = Payment.objects.get(ecpay_merchant_trade_no=merchant_trade_no)
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for merchant_trade_no: {merchant_trade_no}")
            return {'success': False, 'error': 'Payment not found'}
        
        # Log the callback
        PaymentLog.objects.create(
            payment=payment,
            log_type='callback',
            message=f"ECPay callback received - Success: {result['success']}",
            request_data=callback_data,
            response_data=result,
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent', '')
        )
        
        # Update payment based on result
        if result['success']:
            payment.mark_as_paid(result)
            logger.info(f"Payment {payment.payment_id} marked as paid")
        else:
            payment.mark_as_failed(result.get('rtn_msg', ''))
            logger.warning(f"Payment {payment.payment_id} marked as failed: {result.get('rtn_msg', '')}")
        
        return result
    
    def query_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Query payment status from ECPay.
        """
        from .models import Payment
        
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            result = self.ecpay.query_trade_info(payment.ecpay_merchant_trade_no)
            return result
        except Payment.DoesNotExist:
            return None
    
    def _get_order_items_name(self, order) -> str:
        """
        Generate item name string for ECPay from order items.
        ECPay has character limits, so we truncate if necessary.
        """
        items = []
        for item in order.items.all()[:3]:  # Limit to first 3 items
            items.append(item.product_name or (item.product.name if item.product else 'Unknown'))
        
        items_text = '#'.join(items)
        if len(order.items.all()) > 3:
            items_text += f" 等{order.items.count()}項商品"
        
        # ECPay limit is 400 characters
        return items_text[:400] if len(items_text) > 400 else items_text
    
    def _build_return_url(self) -> str:
        """Build return URL for ECPay callbacks."""
        from django.contrib.sites.models import Site
        
        try:
            current_site = Site.objects.get_current()
            domain = f"https://{current_site.domain}"
        except:
            domain = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        return f"{domain}{reverse('payments:ecpay_callback')}"