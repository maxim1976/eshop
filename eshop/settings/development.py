"""
Development settings for eshop project.
"""

from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - can use Railway PostgreSQL or local SQLite
# Set USE_RAILWAY_DB=True in environment to connect to Railway
if config('USE_RAILWAY_DB', default=False, cast=bool):
    # Use Railway PostgreSQL for development
    DATABASES = {
        'default': dj_database_url.config(
            default=config('RAILWAY_DATABASE_URL', default='sqlite:///db.sqlite3')
        )
    }
    print("🌐 Using Railway PostgreSQL database for development")
else:
    # Use local SQLite for development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print("💾 Using local SQLite database for development")

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