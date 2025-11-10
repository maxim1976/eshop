"""
Authentication API views for the Taiwan e-commerce platform.
"""

import uuid
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CustomUser, EmailConfirmationToken, PasswordResetToken, LoginAttempt
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailConfirmationSerializer, UserProfileSerializer
)


class RegisterAPIView(APIView):
    """
    User registration endpoint with email confirmation.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user (active immediately - no email confirmation required)
            user = serializer.save()
            user.is_active = True  # Activate user immediately
            user.save()
            
            # Auto-login user after registration with explicit authentication
            from django.contrib.auth import authenticate
            authenticated_user = authenticate(
                request, 
                username=user.email,  # Use username parameter instead of email
                password=serializer.validated_data['password']  # Use 'password' not 'password1'
            )
            if authenticated_user:
                authenticated_user.backend = 'authentication.backends.EmailBackend'
                login(request, authenticated_user)
            
            return Response({
                'success': True,
                'message': _('註冊成功！歡迎加入日日鮮肉品專賣！'),
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'logged_in': True
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': _('註冊失敗'),
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_confirmation_email(self, user, token, request):
        """Send email confirmation email in user's preferred language."""
        language = user.preferred_language
        
        if language == 'zh-hant':
            subject = '確認您的電子郵件地址 - 日日鮮肉品專賣'
            template = 'emails/confirmation_zh_hant.txt'
        else:
            subject = 'Confirm Your Email Address - 日日鮮肉品專賣'
            template = 'emails/confirmation_en.txt'
        
        # For now, send simple email (templates will be created later)
        message = f"""
        {_('請點擊以下連結確認您的電子郵件地址')}:
        
        {request.build_absolute_uri('/api/auth/confirm-email/')}?token={token.token}
        
        {_('此連結將在48小時後過期')}。
        
        {_('如果您沒有註冊帳戶，請忽略此電子郵件')}。
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class LoginAPIView(APIView):
    """
    User login endpoint with session management.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Check rate limiting
        if self._is_rate_limited(request):
            return Response({
                'success': False,
                'message': _('登入嘗試次數過多，請15分鐘後再試'),
                'retry_after': 900
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember_me = serializer.validated_data.get('remember_me', False)
            
            # Log successful attempt
            self._log_login_attempt(request, user.email, success=True)
            
            # Create session
            login(request, user)
            
            # Set session expiry based on remember_me
            if remember_me:
                # 7 days
                request.session.set_expiry(604800)
                session_expires = timezone.now() + timezone.timedelta(days=7)
            else:
                # Browser session (or default)
                request.session.set_expiry(0)
                session_expires = timezone.now() + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)
            
            return Response({
                'success': True,
                'message': _('登入成功'),
                'data': {
                    'user': UserProfileSerializer(user).data,
                    'session_expires': session_expires.isoformat()
                }
            }, status=status.HTTP_200_OK)
        
        # Log failed attempt
        email = request.data.get('email', '')
        self._log_login_attempt(request, email, success=False)
        
        return Response({
            'success': False,
            'message': _('登入失敗'),
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    def _is_rate_limited(self, request):
        """Check if IP/email is rate limited (3 attempts per 15 minutes)."""
        ip_address = self._get_client_ip(request)
        email = request.data.get('email', '')
        
        # Check failed attempts in last 15 minutes
        time_threshold = timezone.now() - timezone.timedelta(minutes=15)
        
        # Count failed attempts by IP or email
        failed_attempts = LoginAttempt.objects.filter(
            attempted_at__gte=time_threshold,
            success=False
        ).filter(
            models.Q(ip_address=ip_address) | models.Q(email=email)
        ).count()
        
        return failed_attempts >= 3
    
    def _log_login_attempt(self, request, email, success=False):
        """Log login attempt for rate limiting."""
        LoginAttempt.objects.create(
            email=email,
            ip_address=self._get_client_ip(request),
            success=success,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutAPIView(APIView):
    """
    User logout endpoint with session cleanup.
    """
    permission_classes = [AllowAny]  # Allow logout even if not authenticated
    
    def post(self, request):
        # Logout user if authenticated
        if request.user.is_authenticated:
            logout(request)
        
        return Response({
            'success': True,
            'message': _('已成功登出')
        }, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    """
    Password reset request endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Always return success for security (don't reveal if email exists)
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
                
                # Create password reset token
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=str(uuid.uuid4()),
                    ip_address=self._get_client_ip(request)
                )
                
                # Send reset email
                self._send_reset_email(user, reset_token, request)
                
            except CustomUser.DoesNotExist:
                # Don't reveal that user doesn't exist
                pass
            
            return Response({
                'success': True,
                'message': _('如果該電子郵件存在於我們的系統中，您將收到重設密碼的連結')
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': _('密碼重設請求失敗'),
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_reset_email(self, user, token, request):
        """Send password reset email in user's preferred language."""
        language = user.preferred_language
        
        if language == 'zh-hant':
            subject = '重設您的密碼 - 日日鮮肉品專賣'
        else:
            subject = 'Reset Your Password - 日日鮮肉品專賣'
        
        message = f"""
        {_('您已申請重設密碼')}。{_('請點擊以下連結重設您的密碼')}:
        
        {request.build_absolute_uri('/api/auth/password-reset-confirm/')}?token={token.token}
        
        {_('此連結將在4小時後過期')}。
        
        {_('如果您沒有申請密碼重設，請忽略此電子郵件')}。
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PasswordResetConfirmAPIView(APIView):
    """
    Password reset confirmation endpoint with token.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            reset_token = serializer.validated_data['reset_token']
            new_password = serializer.validated_data['new_password']
            
            # Update user password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            return Response({
                'success': True,
                'message': _('密碼重設成功，請使用新密碼登入')
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': _('密碼重設失敗'),
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class EmailConfirmAPIView(APIView):
    """
    Email confirmation endpoint with token.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EmailConfirmationSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            try:
                confirmation_token = EmailConfirmationToken.objects.get(
                    token=token,
                    is_used=False
                )
                
                # Check if token is expired
                if confirmation_token.is_expired():
                    return Response({
                        'success': False,
                        'message': _('電子郵件確認失敗'),
                        'errors': {
                            'token': [_('確認連結已過期')]
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Activate user account
                user = confirmation_token.user
                user.activate_account()
                
                # Mark token as used
                confirmation_token.is_used = True
                confirmation_token.save()
                
                return Response({
                    'success': True,
                    'message': _('電子郵件確認成功，您的帳戶現已啟用')
                }, status=status.HTTP_200_OK)
                
            except EmailConfirmationToken.DoesNotExist:
                return Response({
                    'success': False,
                    'message': _('電子郵件確認失敗'),
                    'errors': {
                        'token': [_('無效或已過期的確認連結')]
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': _('電子郵件確認失敗'),
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    """
    User profile endpoint (authenticated users only).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        
        return Response({
            'success': True,
            'data': {
                'user': serializer.data
            }
        }, status=status.HTTP_200_OK)


# ============================================================================
# WEB TEMPLATE VIEWS (Form-based views for traditional web interface)
# ============================================================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .forms import UserRegistrationForm, UserLoginForm, PasswordResetForm, PasswordResetConfirmForm


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Simplified user registration web form view.
    Creates active users immediately without email confirmation.
    """
    if request.user.is_authenticated:
        return redirect('auth:profile-form')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user (active immediately - no email confirmation required)
            user = form.save()
            user.is_active = True  # Activate user immediately
            user.save()
            
            # Auto-login user after registration with explicit backend
            from django.contrib.auth import authenticate, login as auth_login
            authenticated_user = authenticate(request, username=user.email, password=form.cleaned_data['password1'])
            if authenticated_user:
                auth_login(request, authenticated_user, backend='authentication.backends.EmailBackend')
            
            # Show success message
            messages.success(
                request,
                _('註冊成功！歡迎加入日日鮮肉品專賣！您已自動登入。')
            )
            return redirect('home')  # Redirect to homepage after successful registration
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login web form view.
    Displays login form and handles authentication.
    """
    if request.user.is_authenticated:
        return redirect('auth:profile-form')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Log user in
            auth_login(request, user)
            
            # Set session expiry based on remember_me
            if remember_me:
                # 7 days
                request.session.set_expiry(604800)
            else:
                # Browser session
                request.session.set_expiry(0)
            
            # Success message
            messages.success(request, _('登入成功！歡迎回來。'))
            
            # Redirect to next parameter or profile
            next_url = request.GET.get('next', 'auth:profile-form')
            return redirect(next_url)
    else:
        form = UserLoginForm(request)
    
    return render(request, 'authentication/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    User logout view.
    Logs user out and redirects to login page.
    """
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, _('已成功登出。'))
        return redirect('auth:login-form')
    
    # If GET request, redirect to profile (logout should be POST only)
    return redirect('auth:profile-form')


@require_http_methods(["GET", "POST"])
def password_reset_view(request):
    """
    Password reset request web form view.
    Displays password reset form and sends reset email.
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Always show success message for security (don't reveal if email exists)
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
                
                # Create password reset token
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=str(uuid.uuid4()),
                    ip_address=_get_client_ip_web(request)
                )
                
                # Send reset email
                _send_reset_email_web(user, reset_token, request)
                
            except CustomUser.DoesNotExist:
                # Don't reveal that user doesn't exist
                pass
            
            messages.success(
                request,
                _('如果該電子郵件存在於我們的系統中，您將收到重設密碼的連結。')
            )
            return redirect('auth:login-form')
    else:
        form = PasswordResetForm()
    
    return render(request, 'authentication/password_reset.html', {'form': form})


@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request):
    """
    Password reset confirmation web form view.
    Validates token and allows user to set new password.
    """
    token = request.GET.get('token', '')
    
    # Validate token
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if reset_token.is_expired():
            messages.error(request, _('密碼重設連結已過期。請重新申請。'))
            return redirect('auth:password-reset-form')
        
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                # Update user password
                user = reset_token.user
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                messages.success(request, _('密碼重設成功！請使用新密碼登入。'))
                return redirect('auth:login-form')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'authentication/password_reset_confirm.html', {
            'form': form,
            'token': token
        })
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, _('無效或已過期的密碼重設連結。'))
        return redirect('auth:password-reset-form')


@login_required(login_url='auth:login-form')
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """
    User profile web view.
    Displays and allows editing of user profile.
    """
    user = request.user
    
    if request.method == 'POST':
        # Handle profile updates
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        preferred_language = request.POST.get('preferred_language', 'zh-hant')
        
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.preferred_language = preferred_language
        user.save()
        
        messages.success(request, _('個人資料已更新。'))
        return redirect('auth:profile-form')
    
    return render(request, 'authentication/profile.html', {'user': user})


@require_http_methods(["GET"])
def email_confirm_view(request):
    """
    Email confirmation web view.
    Validates token and activates user account.
    """
    token = request.GET.get('token', '')
    
    try:
        confirmation_token = EmailConfirmationToken.objects.get(
            token=token,
            is_used=False
        )
        
        # Check if token is expired
        if confirmation_token.is_expired():
            return render(request, 'authentication/email_confirm_error.html', {
                'error_message': _('電子郵件確認連結已過期。請重新註冊或聯繫客服。')
            })
        
        # Activate user account
        user = confirmation_token.user
        user.activate_account()
        
        # Mark token as used
        confirmation_token.is_used = True
        confirmation_token.save()
        
        messages.success(request, _('電子郵件確認成功！您的帳戶現已啟用，可以登入了。'))
        return render(request, 'authentication/email_confirmed.html', {
            'user': user
        })
        
    except EmailConfirmationToken.DoesNotExist:
        return render(request, 'authentication/email_confirm_error.html', {
            'error_message': _('無效或已過期的確認連結。請確認您使用的是最新的確認郵件。')
        })


# Helper functions for web views
def _send_confirmation_email_web(user, token, request):
    """Send email confirmation email for web registration."""
    language = user.preferred_language
    
    if language == 'zh-hant':
        subject = '確認您的電子郵件地址 - 日日鮮肉品專賣'
    else:
        subject = 'Confirm Your Email Address - 日日鮮肉品專賣'
    
    # Build absolute URL for confirmation
    confirm_url = request.build_absolute_uri(
        f'/auth/confirm-email/?token={token.token}'
    )
    
    message = f"""
{_('感謝您註冊 日日鮮肉品專賣！')}

{_('請點擊以下連結確認您的電子郵件地址')}:

{confirm_url}

{_('此連結將在48小時後過期')}。

{_('如果您沒有註冊帳戶，請忽略此電子郵件')}。

---
日日鮮肉品專賣 團隊
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def _send_reset_email_web(user, token, request):
    """Send password reset email for web password reset."""
    language = user.preferred_language
    
    if language == 'zh-hant':
        subject = '重設您的密碼 - 日日鮮肉品專賣'
    else:
        subject = 'Reset Your Password - 日日鮮肉品專賣'
    
    # Build absolute URL for password reset
    reset_url = request.build_absolute_uri(
        f'/auth/password-reset-confirm/?token={token.token}'
    )
    
    message = f"""
{_('您已申請重設密碼')}。

{_('請點擊以下連結重設您的密碼')}:

{reset_url}

{_('此連結將在4小時後過期')}。

{_('如果您沒有申請密碼重設，請忽略此電子郵件')}。

---
日日鮮肉品專賣 團隊
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def _get_client_ip_web(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
