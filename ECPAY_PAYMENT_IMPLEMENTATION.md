# ECPay Payment Integration Implementation Guide

## Overview

This guide describes the ECPay payment gateway integration for the Taiwan-based e-commerce platform. ECPay (綠界科技) is Taiwan's leading payment gateway supporting multiple local payment methods.

## Features Implemented

### ✅ Core Payment Features
- **Multiple Payment Methods**: Credit Card, WebATM, ATM Transfer, CVS Code, CVS Barcode
- **Traditional Chinese Support**: Full localization for Taiwan market
- **Secure Transactions**: SHA256 hash verification and HTTPS
- **Payment Status Tracking**: Real-time status updates and callbacks
- **Audit Trail**: Comprehensive logging of all payment transactions

### ✅ Taiwan-Specific Features
- **Local Payment Methods**: ATM, convenience store payments (7-11, FamilyMart, etc.)
- **Traditional Chinese Interface**: Native language support
- **Taiwan Currency**: New Taiwan Dollar (NT$) support
- **PDPA Compliance**: Taiwan Personal Data Protection Act compliance

### ✅ Security Features
- **MAC Verification**: Request/response integrity verification
- **Rate Limiting**: Protection against abuse
- **CSRF Protection**: Django CSRF token validation
- **Input Validation**: Comprehensive data sanitization
- **Secure Callbacks**: Encrypted payment notifications

## Architecture

### Models Structure
```
Payment (Main payment record)
├── PaymentLog (Transaction audit trail)
└── RefundRecord (Refund tracking)
```

### Service Layer
```
PaymentService (High-level payment operations)
└── ECPayService (ECPay API integration)
```

### API Endpoints
- `POST /payments/initiate/<order_id>/` - Payment initiation
- `POST /payments/ecpay/callback/` - ECPay callback handler
- `GET /payments/status/<payment_id>/` - Payment status page
- `GET /payments/api/status/<payment_id>/` - Payment status API

## Payment Flow

### 1. Payment Initiation
```python
# User selects payment method
payment_service = PaymentService()
result = payment_service.create_payment(
    order=order,
    payment_method='Credit',  # or 'ATM', 'CVS', etc.
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT')
)
```

### 2. ECPay Redirect
```html
<!-- Auto-submit form to ECPay -->
<form id="ecpay-form" method="post" action="{{ ecpay_url }}">
    {% for key, value in form_data.items %}
        <input type="hidden" name="{{ key }}" value="{{ value }}">
    {% endfor %}
</form>
```

### 3. Payment Processing
- User completes payment on ECPay platform
- ECPay sends callback to `/payments/ecpay/callback/`
- System verifies MAC and updates payment status
- Order status automatically updated

### 4. Status Tracking
- Real-time status updates via AJAX
- Auto-refresh for pending payments
- Email notifications (optional)

## Configuration

### Environment Variables
```bash
# ECPay Settings
ECPAY_MERCHANT_ID=2000132          # Test merchant ID
ECPAY_HASH_KEY=5294y06JbISpM5x9    # Test hash key
ECPAY_HASH_IV=v77hoKGq4kWxNNIS     # Test hash IV
ECPAY_SANDBOX=True                 # Use sandbox environment

# Site Configuration
SITE_URL=http://localhost:8000     # Your site URL for callbacks
```

### Django Settings
```python
# In settings/base.py
ECPAY_MERCHANT_ID = config('ECPAY_MERCHANT_ID', default='')
ECPAY_HASH_KEY = config('ECPAY_HASH_KEY', default='')
ECPAY_HASH_IV = config('ECPAY_HASH_IV', default='')
ECPAY_SANDBOX = config('ECPAY_SANDBOX', default=True, cast=bool)
SITE_URL = config('SITE_URL', default='http://localhost:8000')
```

## Payment Methods

### 1. Credit Card (信用卡)
- **Method Code**: `Credit`
- **Processing Time**: Immediate
- **Supported Cards**: Visa, MasterCard, JCB
- **Fees**: No additional fees

### 2. WebATM (網路ATM)
- **Method Code**: `WebATM`
- **Processing Time**: Immediate
- **Requirements**: Card reader
- **Fees**: Bank-dependent

### 3. ATM Transfer (ATM轉帳)
- **Method Code**: `ATM`
- **Processing Time**: 3 business days
- **Virtual Account**: Provided after order
- **Fees**: Bank-dependent

### 4. CVS Code Payment (超商代碼)
- **Method Code**: `CVS`
- **Processing Time**: Immediate
- **Stores**: 7-11, FamilyMart, Hi-Life, OK Mart
- **Fees**: NT$30 service fee

### 5. CVS Barcode Payment (超商條碼)
- **Method Code**: `BARCODE`
- **Processing Time**: Immediate
- **Stores**: 7-11, FamilyMart, Hi-Life, OK Mart
- **Fees**: NT$30 service fee

## Security Implementation

### MAC Verification
```python
def generate_check_mac_value(self, parameters):
    # Remove CheckMacValue
    params = {k: v for k, v in parameters.items() if k != 'CheckMacValue'}
    
    # Sort and create query string
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # Add hash key/IV and generate SHA256
    raw_string = f"HashKey={self.hash_key}&{query_string}&HashIV={self.hash_iv}"
    encoded_string = urllib.parse.quote_plus(raw_string, safe='').lower()
    return hashlib.sha256(encoded_string.encode('utf-8')).hexdigest().upper()
```

### Rate Limiting
```python
@ratelimit(key='user', rate='10/5m', method='POST')  # Payment initiation
@ratelimit(key='ip', rate='3/1m', method='POST')     # Callback protection
```

## Testing

### Test Environment
- **ECPay Sandbox**: `https://payment-stage.ecpay.com.tw`
- **Test Merchant ID**: `2000132`
- **Test Credentials**: Provided in `.env.example`

### Test Credit Cards
```
Card Number: 4311-9511-1111-1111
Expiry: 12/25
CVV: 222
```

### Manual Testing Steps
1. Create test order
2. Navigate to payment page
3. Select payment method
4. Complete payment on ECPay sandbox
5. Verify callback processing
6. Check order status update

## Error Handling

### Common Error Codes
- `10100073`: Invalid MAC value
- `10200047`: Invalid merchant trade number
- `10400002`: Payment method not available
- `10500050`: Amount format error

### Error Recovery
```python
def handle_payment_failure(payment, error_code, error_message):
    payment.status = 'failed'
    payment.save()
    
    PaymentLog.objects.create(
        payment=payment,
        log_type='error',
        message=f"Payment failed: {error_code} - {error_message}"
    )
```

## Monitoring and Logging

### Payment Logs
- All API requests/responses logged
- Callback data verified and stored
- Error conditions tracked
- Performance metrics collected

### Admin Interface
- Payment status dashboard
- Transaction search and filtering
- Refund management
- Audit trail viewing

## Production Deployment

### ECPay Account Setup
1. Register at ECPay merchant portal
2. Complete business verification
3. Obtain production credentials
4. Configure webhook endpoints

### Environment Configuration
```bash
# Production settings
ECPAY_SANDBOX=False
ECPAY_MERCHANT_ID=your-production-merchant-id
ECPAY_HASH_KEY=your-production-hash-key
ECPAY_HASH_IV=your-production-hash-iv
SITE_URL=https://yourdomain.com
```

### SSL Certificate
- ECPay requires HTTPS for production
- Callback URLs must use SSL
- Railway.com provides automatic SSL

## API Documentation

### Payment Creation API
```http
POST /payments/api/create/
Content-Type: application/json
Authorization: Bearer <token>

{
    "order_id": 123,
    "payment_method": "Credit",
    "client_back_url": "https://yourdomain.com/orders/123/"
}
```

### Payment Status API
```http
GET /payments/api/status/PAY-20250110-ABCDE/
Authorization: Bearer <token>

Response:
{
    "payment_id": "PAY-20250110-ABCDE",
    "status": "paid",
    "amount": "1500.00",
    "payment_method": "Credit",
    "created_at": "2025-01-10T10:30:00Z"
}
```

## Troubleshooting

### Common Issues
1. **MAC Verification Failed**
   - Check hash key/IV configuration
   - Verify parameter encoding
   - Check parameter sorting

2. **Callback Not Received**
   - Verify SITE_URL configuration
   - Check firewall/security settings
   - Ensure HTTPS in production

3. **Payment Status Not Updated**
   - Check callback endpoint logs
   - Verify MAC verification
   - Check database connectivity

### Debug Mode
Enable detailed logging in development:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'payments.log',
        },
    },
    'loggers': {
        'payments': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Next Steps

### Planned Enhancements
1. **Mobile Payments**: LINE Pay, Apple Pay, Google Pay
2. **Subscription Payments**: Recurring billing support
3. **Multi-currency**: Support for other currencies
4. **Payment Analytics**: Advanced reporting dashboard
5. **Fraud Detection**: Risk scoring and prevention

### Integration Points
- **Order Management**: Automatic order processing
- **Inventory Management**: Stock reservation during payment
- **Customer Service**: Payment inquiry tools
- **Accounting**: Financial reporting integration

## Support

### ECPay Resources
- **Documentation**: https://developers.ecpay.com.tw/
- **Sandbox Environment**: https://payment-stage.ecpay.com.tw/
- **Technical Support**: techsupport@ecpay.com.tw

### Internal Resources
- **Payment Service**: `payments/services.py`
- **Models**: `payments/models.py`
- **API Views**: `payments/views.py`
- **Templates**: `templates/payments/`

---

**Implementation Status**: ✅ Complete and Ready for Testing

**Last Updated**: January 10, 2025
**Version**: 1.0.0