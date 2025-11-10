# GitHub Copilot Instructions for 日日鮮肉品專賣 Authentication System

## Project Context
This is a Taiwan-based e-commerce platform built with Django and Tailwind CSS, deployed on Railway.com. The current feature focus is user registration and authentication with Traditional Chinese primary language support.

## Development Guidelines

### Language and Localization
- **Primary Language**: Traditional Chinese (zh-hant)
- **Secondary Language**: English (en)
- **Template Variables**: Use Django's `{% trans %}` and `{% blocktrans %}` tags
- **Database Content**: Store in user's preferred language
- **Error Messages**: Provide in both languages with fallback

### Django Best Practices
- **Custom User Model**: Extend `AbstractUser` with email as username
- **Authentication**: Use Django's built-in auth with custom extensions
- **Database**: PostgreSQL with proper indexing for performance
- **Sessions**: Database-backed sessions for Railway scaling
- **CSRF**: Always include CSRF protection for forms
- **Migrations**: Create descriptive migration names and comments

### Security Requirements (NON-NEGOTIABLE)
- **Password Policy**: Minimum 8 characters, letters and numbers required
- **Rate Limiting**: 3 login attempts per 15 minutes per IP
- **Token Expiration**: 4 hours for password reset, 48 hours for email confirmation
- **Session Management**: 7 days with remember me, secure cookies
- **Input Validation**: Sanitize all user inputs, use Django forms
- **PDPA Compliance**: Taiwan Personal Data Protection Act requirements

### API Design Standards
- **REST Patterns**: Standard HTTP methods and status codes
- **Response Format**: Consistent JSON structure with success/error fields
- **Headers**: Include CSRF tokens, Accept-Language for i18n
- **Error Handling**: Specific error messages in user's language
- **Rate Limiting**: Implement django-ratelimit for all auth endpoints

### Frontend Guidelines
- **Tailwind CSS**: Use utility classes, no custom CSS without justification
- **Components**: Create reusable template includes for common UI elements
- **Forms**: Use Django forms with proper validation and CSRF
- **JavaScript**: Minimal JS, prefer server-side rendering
- **Accessibility**: Include ARIA labels and semantic HTML

### Testing Requirements
- **Test Coverage**: Minimum 90% for authentication flows
- **Test Types**: Unit tests for models, integration tests for views
- **Security Tests**: Test rate limiting, CSRF protection, input validation
- **Localization Tests**: Verify both Traditional Chinese and English
- **Performance Tests**: API response times under 2 seconds

### Railway.com Deployment
- **Environment Variables**: Use for all secrets and configuration
- **Database**: PostgreSQL addon with connection pooling
- **Static Files**: Configure Django's static file handling
- **Health Checks**: Implement `/health/` endpoint
- **Migrations**: Run automatically on deployment

### Code Style
- **Python**: Follow PEP 8, use type hints where beneficial
- **Django**: Follow Django conventions, use class-based views
- **Templates**: Consistent indentation, semantic HTML structure
- **Comments**: Document complex business logic and security measures
- **Git**: Descriptive commit messages following conventional commits

## File Structure
```
日日鮮肉品專賣/
├── 日日鮮肉品專賣/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/
│   ├── models.py          # CustomUser, tokens, sessions
│   ├── views.py           # API views and form views
│   ├── serializers.py     # DRF serializers
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin interface
│   ├── signals.py         # Post-save handlers
│   └── tests/
├── templates/
│   ├── base.html
│   ├── authentication/
│   └── components/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── locale/
│   ├── zh_Hant/
│   └── en/
└── requirements.txt
```

## Common Patterns

### Model Definition
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=[('zh-hant', '繁體中文'), ('en', 'English')],
        default='zh-hant'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

### API View Pattern
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/15m', method='POST')
def login_view(request):
    # Implementation with proper error handling
    pass
```

### Template Pattern
```html
{% load i18n %}
<form method="post" class="max-w-md mx-auto bg-white p-6 rounded-lg shadow">
    {% csrf_token %}
    <h2 class="text-2xl font-bold mb-4 text-gray-800">
        {% trans "登入" %}
    </h2>
    <!-- Form fields with Tailwind styling -->
</form>
```

## Priority Focus Areas
1. **Security Implementation**: Authentication, authorization, rate limiting
2. **Localization**: Traditional Chinese/English support
3. **Performance**: Fast API responses, optimized queries
4. **PDPA Compliance**: Data protection and user rights
5. **Railway Deployment**: Environment configuration and scaling

When generating code, always consider these guidelines and prioritize security, localization, and performance requirements.