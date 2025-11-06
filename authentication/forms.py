"""
Django forms for authentication web templates.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    """
    User registration form with PDPA consent and language preference.
    """
    
    email = forms.EmailField(
        label=_('電子郵件地址'),
        widget=forms.EmailInput(attrs={
            'placeholder': _('請輸入您的電子郵件地址'),
            'class': 'form-input'
        }),
        help_text=_('用於登入和接收通知的電子郵件地址')
    )
    
    first_name = forms.CharField(
        label=_('名字'),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('請輸入您的名字'),
            'class': 'form-input'
        })
    )
    
    last_name = forms.CharField(
        label=_('姓氏'),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('請輸入您的姓氏'),
            'class': 'form-input'
        })
    )
    
    preferred_language = forms.ChoiceField(
        label=_('偏好語言'),
        choices=[
            ('zh-hant', _('繁體中文')),
            ('en', _('English')),
        ],
        initial='zh-hant',
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        help_text=_('選擇您偏好的介面語言')
    )
    
    pdpa_consent = forms.BooleanField(
        label=_('我同意個人資料保護法條款'),
        required=True,
        help_text=_('您必須同意我們的個人資料保護法條款才能創建帳戶'),
        error_messages={
            'required': _('必須同意個人資料保護法條款才能註冊')
        }
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'preferred_language', 'password1', 'password2', 'pdpa_consent')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': _('請輸入密碼'),
            'class': 'form-input'
        })
        self.fields['password1'].help_text = _('密碼必須至少8個字符，包含字母和數字')
        
        self.fields['password2'].widget.attrs.update({
            'placeholder': _('請再次輸入密碼'),
            'class': 'form-input'
        })
        
        # Remove username field
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('此電子郵件地址已被使用'))
        return email
    
    def save(self, commit=True):
        """Save user with custom fields."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.preferred_language = self.cleaned_data['preferred_language']
        user.pdpa_consent = self.cleaned_data['pdpa_consent']
        user.is_active = False  # Will be activated after email confirmation
        
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    User login form with email and password.
    """
    
    email = forms.EmailField(
        label=_('電子郵件地址'),
        widget=forms.EmailInput(attrs={
            'placeholder': _('請輸入您的電子郵件地址'),
            'class': 'form-input',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label=_('密碼'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('請輸入您的密碼'),
            'class': 'form-input'
        })
    )
    
    remember_me = forms.BooleanField(
        label=_('記住我（7天）'),
        required=False,
        help_text=_('保持登入狀態7天')
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        """Authenticate user credentials."""
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            # Check if user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise forms.ValidationError(_('電子郵件或密碼錯誤'))
            
            # Check if email is confirmed
            if not user.is_email_confirmed:
                raise forms.ValidationError(
                    _('請先確認您的電子郵件地址才能登入。請檢查您的收件箱中的確認郵件。')
                )
            
            # Authenticate user
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(_('電子郵件或密碼錯誤'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('此帳戶已被停用'))
        
        return self.cleaned_data
    
    def get_user(self):
        """Return authenticated user."""
        return self.user_cache


class PasswordResetForm(forms.Form):
    """
    Form for requesting password reset.
    """
    
    email = forms.EmailField(
        label=_('電子郵件地址'),
        widget=forms.EmailInput(attrs={
            'placeholder': _('請輸入您註冊時使用的電子郵件地址'),
            'class': 'form-input',
            'autofocus': True
        }),
        help_text=_('我們將向此電子郵件地址發送重設密碼的連結')
    )
    
    def clean_email(self):
        """Validate email exists (but don't reveal if it doesn't for security)."""
        email = self.cleaned_data.get('email')
        # We don't actually validate if the email exists here for security reasons
        # The view will handle this silently
        return email


class PasswordResetConfirmForm(forms.Form):
    """
    Form for confirming password reset with new password.
    """
    
    new_password1 = forms.CharField(
        label=_('新密碼'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('請輸入新密碼'),
            'class': 'form-input',
            'autofocus': True
        }),
        help_text=_('密碼必須至少8個字符，包含字母和數字')
    )
    
    new_password2 = forms.CharField(
        label=_('確認新密碼'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('請再次輸入新密碼'),
            'class': 'form-input'
        })
    )
    
    def clean(self):
        """Validate password confirmation."""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_('兩次輸入的密碼不符'))
        
        return self.cleaned_data