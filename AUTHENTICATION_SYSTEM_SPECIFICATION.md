# EShop Authentication System - Technical Specification

## 1. Executive Summary

This document provides a comprehensive technical specification for the EShop authentication system - a Taiwan-based e-commerce platform with Traditional Chinese localization and PDPA compliance. The system implements secure user registration, authentication, and session management using Django 4.2 with PostgreSQL backend, deployed on Railway.com.

### 1.1 Key Features
- **Email-based Authentication**: Custom user model with email as primary identifier
- **Bilingual Support**: Traditional Chinese (primary) and English localization
- **PDPA Compliance**: Taiwan Personal Data Protection Act requirements
- **Security-First Design**: Rate limiting, secure sessions, token-based confirmations
- **Multi-Channel Access**: REST API endpoints and web form interfaces

### 1.2 Technology Stack
- **Backend**: Django 4.2.24, Django REST Framework 3.14.0
- **Database**: PostgreSQL with optimized indexes
- **Frontend**: Tailwind CSS 3.x with server-side rendering
- **Deployment**: Railway.com with automated CI/CD
- **Caching**: Database-backed sessions with Redis (production)

## 2. System Architecture

### 2.1 Component Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │    │    API Client    │    │  Admin Panel    │
│  (Templates)    │    │     (REST)       │    │   (Django)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │              Django Application               │
         │  ┌─────────────────────────────────────────┐  │
         │  │         Authentication App              │  │
         │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │  │
         │  │  │ Models  │  │  Views  │  │  Forms  │  │  │
         │  │  └─────────┘  └─────────┘  └─────────┘  │  │
         │  └─────────────────────────────────────────┘  │
         └───────────────────────┬───────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │           PostgreSQL Database                 │
         │  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
         │  │  Users  │  │ Tokens  │  │ Login Logs  │    │
         │  └─────────┘  └─────────┘  └─────────────┘    │
         └───────────────────────────────────────────────┘
```

### 2.2 Data Flow Architecture
1. **Registration Flow**: User → Form/API → Email Token → Confirmation → Activation
2. **Authentication Flow**: Credentials → Rate Limiting → Authentication → Session Creation
3. **Password Reset Flow**: Email Request → Token Generation → Email → Password Update

## 3. Database Schema

### 3.1 CustomUser Model
```sql
CREATE TABLE authentication_customuser (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    preferred_language VARCHAR(10) DEFAULT 'zh-hant',
    is_email_confirmed BOOLEAN DEFAULT FALSE,
    pdpa_consent BOOLEAN DEFAULT FALSE,
    pdpa_consent_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT FALSE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMPTZ DEFAULT NOW(),
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    
    -- Indexes for performance
    INDEX idx_email (email),
    INDEX idx_active_confirmed (is_active, is_email_confirmed)
);
```

### 3.2 Security Token Models
```sql
-- Email Confirmation Tokens (48-hour expiry)
CREATE TABLE authentication_emailconfirmationtoken (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES authentication_customuser(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    
    INDEX idx_token (token),
    INDEX idx_user_used (user_id, is_used),
    INDEX idx_expires (expires_at)
);

-- Password Reset Tokens (4-hour expiry)
CREATE TABLE authentication_passwordresettoken (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES authentication_customuser(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    ip_address INET NOT NULL,
    
    INDEX idx_token (token),
    INDEX idx_user_used (user_id, is_used),
    INDEX idx_expires (expires_at)
);

-- Login Attempt Tracking (Rate Limiting)
CREATE TABLE authentication_loginattempt (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(254) NOT NULL,
    ip_address INET NOT NULL,
    attempted_at TIMESTAMPTZ DEFAULT NOW(),
    success BOOLEAN DEFAULT FALSE,
    user_agent TEXT,
    
    INDEX idx_email_time (email, attempted_at),
    INDEX idx_ip_time (ip_address, attempted_at),
    INDEX idx_attempted (attempted_at)
);
```

### 3.3 User Preferences Model
```sql
CREATE TABLE authentication_userpreferences (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES authentication_customuser(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'zh-hant',
    timezone VARCHAR(50) DEFAULT 'Asia/Taipei',
    email_notifications BOOLEAN DEFAULT TRUE,
    marketing_emails BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 4. API Specification

### 4.1 Authentication Endpoints

#### 4.1.1 User Registration
```http
POST /api/auth/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "first_name": "張",
    "last_name": "三",
    "preferred_language": "zh-hant",
    "pdpa_consent": true
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "註冊成功，請檢查您的電子郵件以確認帳戶",
    "data": {
        "user_id": 123,
        "email": "user@example.com",
        "confirmation_sent": true
    }
}
```

**Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "註冊失敗",
    "errors": {
        "email": ["此電子郵件地址已被使用"],
        "password": ["密碼必須至少8個字符，包含字母和數字"]
    }
}
```

#### 4.1.2 User Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123",
    "remember_me": true
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "登入成功",
    "data": {
        "user": {
            "id": 123,
            "email": "user@example.com",
            "first_name": "張",
            "last_name": "三",
            "preferred_language": "zh-hant",
            "is_email_confirmed": true,
            "date_joined": "2024-01-15T10:30:00Z"
        },
        "session_expires": "2024-01-22T10:30:00Z"
    }
}
```

**Response (429 Too Many Requests):**
```json
{
    "success": false,
    "message": "登入嘗試次數過多，請15分鐘後再試",
    "retry_after": 900
}
```

#### 4.1.3 Email Confirmation
```http
POST /api/auth/confirm-email/
Content-Type: application/json

{
    "token": "uuid-token-from-email"
}
```

#### 4.1.4 Password Reset Request
```http
POST /api/auth/password-reset/
Content-Type: application/json

{
    "email": "user@example.com"
}
```

#### 4.1.5 Password Reset Confirmation
```http
POST /api/auth/password-reset-confirm/
Content-Type: application/json

{
    "token": "uuid-token-from-email",
    "new_password": "NewSecurePass123",
    "new_password_confirm": "NewSecurePass123"
}
```

#### 4.1.6 User Logout
```http
POST /api/auth/logout/
```

#### 4.1.7 User Profile
```http
GET /api/auth/profile/
Authorization: Required (Session-based)
```

### 4.2 Web Form Endpoints

| Endpoint | Method | Template | Purpose |
|----------|--------|----------|---------|
| `/auth/register/` | GET/POST | `authentication/register.html` | Registration form |
| `/auth/login/` | GET/POST | `authentication/login.html` | Login form |
| `/auth/logout/` | POST | - | Logout (redirect) |
| `/auth/profile/` | GET/POST | `authentication/profile.html` | Profile management |
| `/auth/password-reset/` | GET/POST | `authentication/password_reset.html` | Password reset request |
| `/auth/password-reset-confirm/` | GET/POST | `authentication/password_reset_confirm.html` | Password reset form |
| `/auth/confirm-email/` | GET | `authentication/email_confirmed.html` | Email confirmation |

## 5. Security Implementation

### 5.1 Authentication Backend
```python
# authentication/backends.py
class EmailBackend(BaseBackend):
    """Custom authentication backend using email instead of username."""
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except CustomUser.DoesNotExist:
            # Run default password hasher to mitigate timing attacks
            CustomUser().set_password(password)
        return None
```

### 5.2 Rate Limiting Implementation
```python
# Rate limiting: 3 attempts per 15 minutes per IP/email
@ratelimit(key='ip', rate='3/15m', method='POST', block=True)
@ratelimit(key='post:email', rate='3/15m', method='POST', block=True)
def login_view(request):
    # Login logic with rate limiting
    pass
```

### 5.3 Password Validation
```python
# authentication/validators.py
class AlphanumericPasswordValidator:
    """Require passwords to contain both letters and numbers."""
    
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError(_('密碼必須包含至少一個字母'))
        if not re.search(r'\d', password):
            raise ValidationError(_('密碼必須包含至少一個數字'))
```

### 5.4 Token Security
- **Email Confirmation**: 48-hour expiration with UUID4 tokens
- **Password Reset**: 4-hour expiration with IP address tracking
- **Session Management**: 7-day expiration with "Remember Me" option
- **CSRF Protection**: Required for all state-changing operations

## 6. Localization and PDPA Compliance

### 6.1 Language Support
```python
# Django settings for internationalization
LANGUAGES = [
    ('en', 'English'),
    ('zh-hant', '繁體中文'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']
USE_I18N = True
USE_L10N = True
```

### 6.2 PDPA Implementation
```python
# Model field for consent tracking
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
```

### 6.3 Email Templates
- Traditional Chinese templates: `emails/confirmation_zh_hant.txt`
- English templates: `emails/confirmation_en.txt`
- Automatic language detection based on user preference

## 7. Performance Optimization

### 7.1 Database Indexes
```sql
-- Optimized indexes for common queries
CREATE INDEX idx_user_email ON authentication_customuser(email);
CREATE INDEX idx_user_active_confirmed ON authentication_customuser(is_active, is_email_confirmed);
CREATE INDEX idx_token_lookup ON authentication_emailconfirmationtoken(token);
CREATE INDEX idx_login_attempts_ip_time ON authentication_loginattempt(ip_address, attempted_at);
```

### 7.2 Query Optimization
- **Select Related**: Use for foreign key relationships
- **Prefetch Related**: Use for many-to-many relationships
- **Database Connection Pooling**: Configured for Railway PostgreSQL

### 7.3 Caching Strategy
```python
# Production caching with Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Rate limiting cache
RATELIMIT_USE_CACHE = 'default'
```

## 8. Testing Strategy

### 8.1 Test Coverage Requirements
- **Minimum Coverage**: 90% for authentication flows
- **Critical Paths**: 100% coverage for security-related functions
- **Performance Tests**: API response times under 2 seconds

### 8.2 Test Categories
```python
# Unit Tests
class CustomUserModelTests(TestCase):
    """Test custom user model functionality."""
    
class AuthenticationBackendTests(TestCase):
    """Test email-based authentication backend."""

# Integration Tests  
class RegistrationFlowTests(TestCase):
    """Test complete registration and confirmation flow."""
    
class LoginFlowTests(TestCase):
    """Test login flow with rate limiting."""

# Security Tests
class RateLimitingTests(TestCase):
    """Test rate limiting implementation."""
    
class CSRFProtectionTests(TestCase):
    """Test CSRF protection on all forms."""

# Localization Tests
class InternationalizationTests(TestCase):
    """Test Traditional Chinese and English localization."""
```

### 8.3 Test Data Management
```python
# Factory pattern for test data
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    preferred_language = 'zh-hant'
    pdpa_consent = True
    is_email_confirmed = True
    is_active = True
```

## 9. Deployment Configuration

### 9.1 Railway.com Setup
```json
// railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### 9.2 Environment Variables
```bash
# Required environment variables for Railway deployment
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eshop.com

# ECPay payment gateway
ECPAY_MERCHANT_ID=your-merchant-id
ECPAY_HASH_KEY=your-hash-key
ECPAY_HASH_IV=your-hash-iv
ECPAY_SANDBOX=False

# Site configuration
SITE_URL=https://your-domain.railway.app
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,localhost
```

### 9.3 Static Files Configuration
```python
# Production static files settings
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Middleware for serving static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files
    # ... other middleware
]
```

## 10. Monitoring and Logging

### 10.1 Application Logging
```python
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'authentication': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 10.2 Health Check Endpoint
```python
# Health check for Railway monitoring
def health_check(request):
    """Simple health check endpoint for monitoring."""
    try:
        # Test database connection
        from django.db import connection
        connection.ensure_connection()
        
        # Test cache connection
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'cache': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

### 10.3 Security Monitoring
- **Failed Login Attempts**: Automatic logging and alerting
- **Rate Limit Violations**: Track and monitor suspicious activity
- **Token Usage**: Monitor token generation and usage patterns
- **PDPA Compliance**: Log consent changes and data access

## 11. Migration and Maintenance

### 11.1 Database Migrations
```python
# Example migration for adding new security features
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_password_change',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddIndex(
            model_name='loginattempt',
            index=models.Index(fields=['attempted_at'], name='auth_login_attempt_time_idx'),
        ),
    ]
```

### 11.2 Data Cleanup Tasks
```python
# Management command for cleaning expired tokens
from django.core.management.base import BaseCommand
from django.utils import timezone
from authentication.models import EmailConfirmationToken, PasswordResetToken

class Command(BaseCommand):
    help = 'Clean up expired authentication tokens'
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        # Delete expired email confirmation tokens
        email_tokens_deleted = EmailConfirmationToken.objects.filter(
            expires_at__lt=now
        ).delete()[0]
        
        # Delete expired password reset tokens
        reset_tokens_deleted = PasswordResetToken.objects.filter(
            expires_at__lt=now
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleaned up {email_tokens_deleted} email tokens and '
                f'{reset_tokens_deleted} reset tokens'
            )
        )
```

### 11.3 Backup Strategy
- **Database Backups**: Automated daily backups via Railway
- **Static Files**: Version controlled in Git repository
- **Configuration**: Environment variables documented and backed up
- **User Data**: PDPA-compliant export functionality

## 12. Future Enhancements

### 12.1 Planned Features
1. **Two-Factor Authentication**: SMS or TOTP-based 2FA
2. **Social Login**: Google, Facebook, LINE integration
3. **Advanced Analytics**: User behavior tracking and insights
4. **Mobile App Support**: JWT-based authentication for mobile clients

### 12.2 Scalability Considerations
1. **Microservices**: Extract authentication to separate service
2. **CDN Integration**: Serve static assets via CDN
3. **Load Balancing**: Multiple Railway deployments with load balancer
4. **Database Sharding**: Horizontal scaling for large user bases

## 13. Conclusion

The EShop authentication system provides a robust, secure, and scalable foundation for the Taiwan e-commerce platform. With comprehensive security measures, PDPA compliance, and bilingual support, the system is well-positioned to handle production workloads while maintaining excellent user experience and regulatory compliance.

The modular design allows for easy extension and maintenance, while the comprehensive testing strategy ensures reliability and security. The deployment on Railway.com provides scalability and ease of management, making it suitable for both development and production environments.

---

**Document Version**: 1.0  
**Last Updated**: January 2024  
**Next Review**: June 2024