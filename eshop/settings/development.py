"""
Development settings for eshop project.
"""

from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - Railway PostgreSQL for both development and production
# Using the same database for consistency
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', 
                      default='postgresql://postgres:lAljkuzMrvOdlmYAtgaSddmbwosCnwQr@yamabiko.proxy.rlwy.net:13209/railway')
    )
}

print("🐘 Using Railway PostgreSQL database for development")

# Email Backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Session settings for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]