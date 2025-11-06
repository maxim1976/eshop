"""
Authentication URL patterns for API endpoints and web templates.
"""

from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    # API endpoints
    path('api/auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('api/auth/password-reset/', views.PasswordResetAPIView.as_view(), name='password-reset'),
    path('api/auth/password-reset-confirm/', views.PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('api/auth/confirm-email/', views.EmailConfirmAPIView.as_view(), name='confirm-email'),
    path('api/auth/profile/', views.ProfileAPIView.as_view(), name='profile'),
    
    # Web template endpoints
    path('auth/register/', views.register_view, name='register-form'),
    path('auth/login/', views.login_view, name='login-form'),
    path('auth/logout/', views.logout_view, name='logout-form'),
    path('auth/password-reset/', views.password_reset_view, name='password-reset-form'),
    path('auth/password-reset-confirm/', views.password_reset_confirm_view, name='password-reset-confirm-form'),
    path('auth/profile/', views.profile_view, name='profile-form'),
    path('auth/confirm-email/', views.email_confirm_view, name='confirm-email-form'),
]