"""
Forms for order processing and checkout.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .models import Order


class CheckoutForm(forms.Form):
    """
    Checkout form for order creation.
    """
    
    # Shipping Information
    recipient_name = forms.CharField(
        label=_('收件人姓名 / Recipient Name'),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': _('請輸入收件人姓名 / Enter recipient name')
        })
    )
    
    recipient_phone = forms.CharField(
        label=_('收件人電話 / Recipient Phone'),
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[\d\-\+\(\)\s]+$',
                message=_('請輸入有效的電話號碼 / Please enter a valid phone number')
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': _('例如: 0912-345-678 / e.g. 0912-345-678')
        })
    )
    
    # Taiwan Address Fields
    postal_code = forms.CharField(
        label=_('郵遞區號 / Postal Code'),
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{3,5}$',
                message=_('請輸入有效的郵遞區號 / Please enter a valid postal code')
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': _('例如: 10048 / e.g. 10048')
        })
    )
    
    city = forms.CharField(
        label=_('縣市 / City'),
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': _('例如: 台北市 / e.g. Taipei City')
        })
    )
    
    district = forms.CharField(
        label=_('區域 / District'),
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': _('例如: 中正區 / e.g. Zhongzheng District')
        })
    )
    
    address = forms.CharField(
        label=_('詳細地址 / Detailed Address'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': _('例如: 重慶南路一段122號 / e.g. No.122, Sec.1, Chongqing S. Rd.')
        })
    )
    
    # Shipping Method
    shipping_method = forms.ChoiceField(
        label=_('配送方式 / Shipping Method'),
        choices=Order.SHIPPING_METHOD_CHOICES,
        initial='home_delivery',
        widget=forms.RadioSelect(attrs={
            'class': 'shipping-method-radio'
        })
    )
    
    # Payment Method (will be handled in payment system)
    payment_method = forms.ChoiceField(
        label=_('付款方式 / Payment Method'),
        choices=Order.PAYMENT_METHOD_CHOICES,
        initial='credit_card',
        widget=forms.RadioSelect(attrs={
            'class': 'payment-method-radio'
        })
    )
    
    # Notes
    notes = forms.CharField(
        label=_('備註 / Notes'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'rows': 3,
            'placeholder': _('有任何特別需求請在此註明 / Please specify any special requirements')
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill fields if user has previous orders
        if self.user:
            try:
                last_order = Order.objects.filter(user=self.user).latest('created_at')
                self.fields['recipient_name'].initial = last_order.recipient_name
                self.fields['recipient_phone'].initial = last_order.recipient_phone
                self.fields['postal_code'].initial = last_order.shipping_postal_code
                self.fields['city'].initial = last_order.shipping_city
                self.fields['district'].initial = last_order.shipping_district
                self.fields['address'].initial = last_order.shipping_address
                self.fields['shipping_method'].initial = last_order.shipping_method
            except Order.DoesNotExist:
                pass
    
    def clean_recipient_name(self):
        name = self.cleaned_data.get('recipient_name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError(_('收件人姓名至少需要2個字元 / Recipient name must be at least 2 characters'))
        return name.strip()
    
    def clean_recipient_phone(self):
        phone = self.cleaned_data.get('recipient_phone')
        # Remove spaces and dashes for validation
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
        
        if not clean_phone.isdigit():
            raise forms.ValidationError(_('電話號碼只能包含數字和符號 / Phone number can only contain digits and symbols'))
        
        if len(clean_phone) < 8 or len(clean_phone) > 15:
            raise forms.ValidationError(_('電話號碼長度不正確 / Phone number length is incorrect'))
        
        return phone
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code.isdigit():
            raise forms.ValidationError(_('郵遞區號只能包含數字 / Postal code can only contain digits'))
        return postal_code
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate shipping method and address combination
        shipping_method = cleaned_data.get('shipping_method')
        address = cleaned_data.get('address')
        
        if shipping_method == 'home_delivery' and not address:
            raise forms.ValidationError(_('宅配需要提供詳細地址 / Home delivery requires detailed address'))
        
        return cleaned_data