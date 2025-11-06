"""
DRF serializers for authentication API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, EmailConfirmationToken, PasswordResetToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with PDPA consent and password confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text=_('密碼必須至少8個字符，包含字母和數字')
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text=_('確認密碼必須與密碼相符')
    )
    pdpa_consent = serializers.BooleanField(
        required=True,
        help_text=_('必須同意個人資料保護法條款才能註冊')
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 
            'last_name', 'preferred_language', 'pdpa_consent'
        ]
        extra_kwargs = {
            'email': {'help_text': _('用於登入和接收通知的電子郵件地址')},
            'first_name': {'help_text': _('用戶的名字')},
            'last_name': {'help_text': _('用戶的姓氏')},
            'preferred_language': {'help_text': _('偏好的介面語言')},
        }
    
    def validate_pdpa_consent(self, value):
        """Validate PDPA consent is True."""
        if not value:
            raise serializers.ValidationError(
                _('必須同意個人資料保護法條款才能創建帳戶')
            )
        return value
    
    def validate(self, attrs):
        """Validate password confirmation matches."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _('確認密碼與密碼不符')
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with email confirmation required."""
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm')
        
        # Create user (inactive by default)
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            preferred_language=validated_data.get('preferred_language', 'zh-hant'),
            pdpa_consent=validated_data['pdpa_consent'],
            is_active=False,  # Will be activated after email confirmation
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email and password.
    """
    email = serializers.EmailField(
        help_text=_('註冊時使用的電子郵件地址')
    )
    password = serializers.CharField(
        write_only=True,
        help_text=_('帳戶密碼')
    )
    remember_me = serializers.BooleanField(
        default=False,
        help_text=_('是否延長登入會話期限至7天')
    )
    
    def validate(self, attrs):
        """Validate user credentials and account status."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Check if user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({
                    'credentials': _('電子郵件或密碼錯誤')
                })
            
            # Check if email is confirmed
            if not user.is_email_confirmed:
                raise serializers.ValidationError({
                    'email_confirmation': _('請先確認您的電子郵件地址才能登入')
                })
            
            # Authenticate user
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({
                    'credentials': _('電子郵件或密碼錯誤')
                })
            
            attrs['user'] = user
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField(
        help_text=_('註冊時使用的電子郵件地址')
    )
    
    def validate_email(self, value):
        """Always return the email (don't reveal if user exists)."""
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation with token.
    """
    token = serializers.CharField(
        help_text=_('從重設密碼電子郵件中獲取的令牌')
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text=_('新密碼必須至少8個字符，包含字母和數字')
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        help_text=_('確認新密碼必須與新密碼相符')
    )
    
    def validate(self, attrs):
        """Validate token and password confirmation."""
        token = attrs.get('token')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # Check password confirmation
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': _('確認密碼與新密碼不符')
            })
        
        # Validate token
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': _('無效或已過期的重設連結')
            })
        
        # Check if token is expired
        if reset_token.is_expired():
            raise serializers.ValidationError({
                'token': _('重設連結已過期，請重新申請密碼重設')
            })
        
        attrs['reset_token'] = reset_token
        return attrs


class EmailConfirmationSerializer(serializers.Serializer):
    """
    Serializer for email confirmation with token.
    """
    token = serializers.CharField(
        help_text=_('從確認電子郵件中獲取的令牌')
    )
    
    def validate_token(self, value):
        """Validate email confirmation token."""
        try:
            confirmation_token = EmailConfirmationToken.objects.get(
                token=value, 
                is_used=False
            )
        except EmailConfirmationToken.DoesNotExist:
            raise serializers.ValidationError(
                _('無效或已過期的確認連結')
            )
        
        # Check if token is expired
        if confirmation_token.is_expired():
            raise serializers.ValidationError(
                _('確認連結已過期，請重新申請電子郵件確認')
            )
        
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information (read-only).
    """
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'preferred_language', 'is_email_confirmed', 'date_joined'
        ]
        read_only_fields = fields