"""
Django admin configuration for authentication models.
Provides comprehensive admin interface for user management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    CustomUser, 
    EmailConfirmationToken, 
    PasswordResetToken, 
    LoginAttempt
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom user admin interface."""
    
    # Display configuration
    list_display = (
        'email', 
        'get_full_name_display', 
        'preferred_language',
        'is_email_confirmed',
        'is_active', 
        'is_staff',
        'date_joined',
        'last_login'
    )
    
    list_filter = (
        'is_active', 
        'is_staff', 
        'is_superuser',
        'is_email_confirmed',
        'preferred_language',
        'pdpa_consent',
        'date_joined',
        'last_login'
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Form configuration
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'preferred_language')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser',
                'groups', 
                'user_permissions'
            ),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Account Status', {
            'fields': ('is_email_confirmed',)
        }),
        ('Privacy', {
            'fields': ('pdpa_consent', 'pdpa_consent_date')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'preferred_language')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'pdpa_consent_date')
    
    # Custom methods
    def get_full_name_display(self, obj):
        """Display full name with fallback to email."""
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else obj.email
    get_full_name_display.short_description = 'Full Name'
    
    # Actions
    actions = ['confirm_emails', 'activate_users', 'deactivate_users']
    
    def confirm_emails(self, request, queryset):
        """Bulk confirm email addresses."""
        updated = queryset.update(
            is_email_confirmed=True, 
            is_active=True
        )
        self.message_user(request, f'Confirmed email addresses for {updated} users')
    confirm_emails.short_description = 'Confirm email for selected users'
    
    def activate_users(self, request, queryset):
        """Bulk activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Activated {updated} user accounts')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {updated} user accounts')
    deactivate_users.short_description = 'Deactivate selected users'


@admin.register(EmailConfirmationToken)
class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    """Email confirmation token admin interface."""
    
    list_display = (
        'user_email',
        'email', 
        'token_short',
        'is_used', 
        'is_expired',
        'created_at'
    )
    
    list_filter = (
        'is_used', 
        'created_at'
    )
    
    search_fields = ('user__email', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'is_expired')
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        """Display shortened token."""
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Confirmation Token'
    
    def is_expired(self, obj):
        """Check if token is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Password reset token admin interface."""
    
    list_display = (
        'user_email',
        'token_short',
        'is_used', 
        'is_expired',
        'created_at'
    )
    
    list_filter = (
        'is_used', 
        'created_at'
    )
    
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'is_expired')
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        """Display shortened token."""
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Reset Token'
    
    def is_expired(self, obj):
        """Check if token is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Login attempt admin interface."""
    
    list_display = (
        'email',
        'ip_address',
        'user_agent_short',
        'success',
        'attempted_at'
    )
    
    list_filter = (
        'success',
        'attempted_at'
    )
    
    search_fields = ('email', 'ip_address')
    ordering = ('-attempted_at',)
    readonly_fields = ('attempted_at',)
    
    def user_agent_short(self, obj):
        """Display shortened user agent."""
        if obj.user_agent and len(obj.user_agent) > 50:
            return f"{obj.user_agent[:50]}..."
        return obj.user_agent or "Unknown"
    user_agent_short.short_description = 'Browser'
    
    # Custom actions
    actions = ['clear_old_attempts']
    
    def clear_old_attempts(self, request, queryset):
        """Clear login attempts older than 30 days."""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        old_attempts = LoginAttempt.objects.filter(attempted_at__lt=cutoff_date)
        count = old_attempts.count()
        old_attempts.delete()
        self.message_user(request, f'Cleared {count} old login attempt records')
    clear_old_attempts.short_description = 'Clear login records older than 30 days'


# Admin site customization
admin.site.site_header = 'EShop Administration'
admin.site.site_title = 'EShop Admin'
admin.site.index_title = 'Welcome to EShop Management System'
