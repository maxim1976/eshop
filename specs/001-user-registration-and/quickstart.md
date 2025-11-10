# Quickstart: User Registration and Authentication System

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (for Tailwind CSS)
- PostgreSQL (or use Railway.com for development)
- Git

### Local Development
```bash
# Clone and setup
git checkout 001-user-registration-and
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework django-cors-headers
pip install psycopg2-binary python-decouple django-ratelimit
npm install -D tailwindcss @tailwindcss/forms

# Environment setup
cp .env.example .env
# Edit .env with your database and email settings

# Database setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/日日鮮肉品專賣
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yoursite.com
LANGUAGE_CODE=zh-hant
TIME_ZONE=Asia/Taipei
```

## Testing Scenarios

### 1. User Registration Flow
**Scenario**: New customer creates account

**Steps**:
1. Navigate to `/register/`
2. Fill form with valid email and password (8+ chars, letters+numbers)
3. Accept PDPA consent checkbox
4. Submit form
5. Verify success message in Traditional Chinese
6. Check email for confirmation link
7. Click confirmation link
8. Verify account activation

**Expected Results**:
- Account created but inactive initially
- Confirmation email sent in Traditional Chinese
- Account activated after email confirmation
- User can log in after activation

### 2. Login and Session Management
**Scenario**: Registered user logs in with remember me

**Steps**:
1. Navigate to `/login/`
2. Enter valid email and password
3. Check "記住我" (remember me) checkbox
4. Submit form
5. Verify redirect to dashboard
6. Close browser and reopen
7. Navigate to protected page
8. Verify still logged in (7-day session)

**Expected Results**:
- Successful login with Traditional Chinese messages
- Session persists for 7 days with remember me
- User profile accessible at `/profile/`

### 3. Password Reset Flow
**Scenario**: User forgot password

**Steps**:
1. Navigate to `/password-reset/`
2. Enter registered email address
3. Submit form
4. Check email for reset link (4-hour expiration)
5. Click reset link
6. Enter new password (meeting requirements)
7. Submit new password
8. Verify redirect to login page
9. Log in with new password

**Expected Results**:
- Reset email sent in user's preferred language
- Token expires after 4 hours
- Password successfully updated
- Can log in with new password

### 4. Rate Limiting Protection
**Scenario**: Brute force login prevention

**Steps**:
1. Navigate to `/login/`
2. Enter valid email but wrong password
3. Submit 3 times rapidly
4. Attempt 4th login
5. Verify rate limiting message
6. Wait 15 minutes
7. Attempt login again

**Expected Results**:
- First 3 attempts show "incorrect password"
- 4th attempt shows rate limiting message in Traditional Chinese
- Login blocked for 15 minutes
- Can attempt again after cooldown

### 5. Language Switching
**Scenario**: User changes language preference

**Steps**:
1. Log in with Traditional Chinese interface
2. Navigate to profile settings
3. Change language to English
4. Save preferences
5. Navigate to different pages
6. Verify interface language changed
7. Test password reset in English

**Expected Results**:
- Interface switches to English immediately
- Email notifications sent in English
- Error messages displayed in English
- Language preference persisted

## API Testing

### Authentication Endpoints
```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "測試",
    "last_name": "用戶",
    "preferred_language": "zh-hant",
    "pdpa_consent": true
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "remember_me": true
  }'

# Get profile (requires session cookie)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Accept-Language: zh-hant" \
  --cookie "sessionid=your-session-id"

# Password reset
curl -X POST http://localhost:8000/api/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Railway.com Deployment

### Deployment Configuration
```json
// railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Production Environment Variables
```
DEBUG=False
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://[railway-provided]
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=[sendgrid-api-key]
ALLOWED_HOSTS=yourapp.railway.app
CSRF_TRUSTED_ORIGINS=https://yourapp.railway.app
```

### Deployment Steps
1. Push to main branch
2. Connect Railway to GitHub repository
3. Add PostgreSQL database addon
4. Configure environment variables
5. Deploy and run migrations
6. Test production endpoints

## Security Checklist

- [ ] HTTPS enforced in production
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Password complexity enforced
- [ ] Session security configured
- [ ] Email confirmation required
- [ ] Token expiration implemented
- [ ] PDPA compliance features
- [ ] SQL injection protection (Django ORM)
- [ ] XSS protection (template escaping)

## Performance Targets

- Authentication API responses: < 2 seconds
- Page load times: < 3 seconds on 3G
- Database queries: < 100ms average
- Email delivery: < 30 seconds
- Rate limit recovery: 15 minutes
- Session cleanup: Daily automated job