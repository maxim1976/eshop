"""
Authentication models for the Taiwan e-commerce platform.
Includes custom user model and related authentication entities.
"""

import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    """
    Custom user manager for email-based authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError(_('電子郵件地址是必需的'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_confirmed', True)
        extra_fields.setdefault('pdpa_consent', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超級用戶必須設置 is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超級用戶必須設置 is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model with email as username and Taiwan localization support.
    """
    
    # Remove username field and use email instead
    username = None
    email = models.EmailField(
        _('電子郵件地址'),
        unique=True,
        help_text=_('用於登入的電子郵件地址')
    )
    
    # Additional fields for Taiwan e-commerce
    preferred_language = models.CharField(
        _('偏好語言'),
        max_length=10,
        choices=[
            ('zh-hant', _('繁體中文')),
            ('en', _('English')),
        ],
        default='zh-hant',
        help_text=_('使用者介面和電子郵件的偏好語言')
    )
    
    is_email_confirmed = models.BooleanField(
        _('電子郵件已確認'),
        default=False,
        help_text=_('用戶是否已確認其電子郵件地址')
    )
    
    pdpa_consent = models.BooleanField(
        _('PDPA同意'),
        default=False,
        help_text=_('用戶是否同意個人資料保護法條款')
    )
    
    pdpa_consent_date = models.DateTimeField(
        _('PDPA同意日期'),
        null=True,
        blank=True,
        help_text=_('用戶同意PDPA條款的日期和時間')
    )
    
    # Override is_active to require email confirmation
    is_active = models.BooleanField(
        _('帳戶啟用'),
        default=False,
        help_text=_('帳戶是否已啟用（需要電子郵件確認）')
    )
    
    # Use custom manager
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('用戶')
        verbose_name_plural = _('用戶')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_email_confirmed']),
        ]
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """Override save to set PDPA consent date."""
        if self.pdpa_consent and not self.pdpa_consent_date:
            self.pdpa_consent_date = timezone.now()
        super().save(*args, **kwargs)
    
    def activate_account(self):
        """Activate account after email confirmation."""
        self.is_active = True
        self.is_email_confirmed = True
        self.save(update_fields=['is_active', 'is_email_confirmed'])


class EmailConfirmationToken(models.Model):
    """
    Temporary tokens for email verification with 48-hour expiration.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_('用戶'),
        related_name='email_confirmation_tokens'
    )
    
    token = models.CharField(
        _('確認令牌'),
        max_length=255,
        unique=True,
        default=uuid.uuid4,
        help_text=_('用於電子郵件確認的唯一令牌')
    )
    
    email = models.EmailField(
        _('確認的電子郵件'),
        help_text=_('正在確認的電子郵件地址')
    )
    
    created_at = models.DateTimeField(
        _('創建時間'),
        auto_now_add=True
    )
    
    expires_at = models.DateTimeField(
        _('過期時間'),
        help_text=_('令牌過期的日期和時間')
    )
    
    is_used = models.BooleanField(
        _('已使用'),
        default=False,
        help_text=_('令牌是否已被使用')
    )
    
    class Meta:
        verbose_name = _('電子郵件確認令牌')
        verbose_name_plural = _('電子郵件確認令牌')
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Set expiration time to 48 hours from creation."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Email confirmation for {self.user.email}"


class PasswordResetToken(models.Model):
    """
    Temporary tokens for password reset requests with 4-hour expiration.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_('用戶'),
        related_name='password_reset_tokens'
    )
    
    token = models.CharField(
        _('重設令牌'),
        max_length=255,
        unique=True,
        default=uuid.uuid4,
        help_text=_('用於密碼重設的唯一令牌')
    )
    
    created_at = models.DateTimeField(
        _('創建時間'),
        auto_now_add=True
    )
    
    expires_at = models.DateTimeField(
        _('過期時間'),
        help_text=_('令牌過期的日期和時間')
    )
    
    is_used = models.BooleanField(
        _('已使用'),
        default=False,
        help_text=_('令牌是否已被使用')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP地址'),
        help_text=_('發出重設請求的IP地址')
    )
    
    class Meta:
        verbose_name = _('密碼重設令牌')
        verbose_name_plural = _('密碼重設令牌')
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Set expiration time to 4 hours from creation."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=4)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if token has expired."""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Password reset for {self.user.email}"


class LoginAttempt(models.Model):
    """
    Track failed login attempts for rate limiting (3 per 15 minutes).
    """
    
    email = models.EmailField(
        _('嘗試的電子郵件'),
        help_text=_('嘗試登入的電子郵件地址')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP地址'),
        help_text=_('發出登入嘗試的IP地址')
    )
    
    attempted_at = models.DateTimeField(
        _('嘗試時間'),
        auto_now_add=True
    )
    
    success = models.BooleanField(
        _('成功'),
        default=False,
        help_text=_('登入嘗試是否成功')
    )
    
    user_agent = models.TextField(
        _('用戶代理'),
        blank=True,
        help_text=_('發出請求的瀏覽器用戶代理字符串')
    )
    
    class Meta:
        verbose_name = _('登入嘗試')
        verbose_name_plural = _('登入嘗試')
        indexes = [
            models.Index(fields=['email', 'attempted_at']),
            models.Index(fields=['ip_address', 'attempted_at']),
            models.Index(fields=['attempted_at']),
        ]
    
    def __str__(self):
        status = "成功" if self.success else "失敗"
        return f"{self.email} - {status} ({self.attempted_at})"


class UserPreferences(models.Model):
    """
    Store user preferences and settings.
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_('用戶'),
        related_name='preferences'
    )
    
    language = models.CharField(
        _('語言'),
        max_length=10,
        choices=[
            ('zh-hant', _('繁體中文')),
            ('en', _('English')),
        ],
        default='zh-hant'
    )
    
    timezone = models.CharField(
        _('時區'),
        max_length=50,
        default='Asia/Taipei',
        help_text=_('用戶的時區設定')
    )
    
    email_notifications = models.BooleanField(
        _('電子郵件通知'),
        default=True,
        help_text=_('是否接收電子郵件通知')
    )
    
    marketing_emails = models.BooleanField(
        _('行銷電子郵件'),
        default=False,
        help_text=_('是否接收行銷電子郵件')
    )
    
    created_at = models.DateTimeField(
        _('創建時間'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('更新時間'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('用戶偏好設定')
        verbose_name_plural = _('用戶偏好設定')
    
    def __str__(self):
        return f"{self.user.email} preferences"
