# Authentication API Contract

## Base URL
- Development: `http://localhost:8000/api/auth/`
- Production: `https://[railway-app].railway.app/api/auth/`

## Common Headers
```
Content-Type: application/json
Accept: application/json
Accept-Language: zh-hant,en;q=0.9
X-CSRFToken: [csrf_token] (for state-changing operations)
```

## Authentication Endpoints

### POST /register/
**Purpose**: Register new user account with email confirmation

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "張",
  "last_name": "小明",
  "preferred_language": "zh-hant",
  "pdpa_consent": true
}
```

**Success Response (201)**:
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

**Error Response (400)**:
```json
{
  "success": false,
  "message": "註冊失敗",
  "errors": {
    "email": ["此電子郵件已被使用"],
    "password": ["密碼必須至少8個字符，包含字母和數字"]
  }
}
```

### POST /login/
**Purpose**: Authenticate user and create session

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "remember_me": true
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "登入成功",
  "data": {
    "user": {
      "id": 123,
      "email": "user@example.com",
      "first_name": "張",
      "last_name": "小明",
      "preferred_language": "zh-hant"
    },
    "session_expires": "2025-02-03T16:39:00Z"
  }
}
```

**Error Response (401)**:
```json
{
  "success": false,
  "message": "電子郵件或密碼錯誤",
  "errors": {
    "credentials": ["無效的登入憑證"]
  }
}
```

**Rate Limited Response (429)**:
```json
{
  "success": false,
  "message": "登入嘗試次數過多，請15分鐘後再試",
  "retry_after": 900
}
```

### POST /logout/
**Purpose**: End user session

**Request**: No body required, uses session cookie

**Success Response (200)**:
```json
{
  "success": true,
  "message": "已成功登出"
}
```

### POST /password-reset/
**Purpose**: Request password reset email

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Success Response (200)** (always returns success for security):
```json
{
  "success": true,
  "message": "如果該電子郵件存在於我們的系統中，您將收到重設密碼的連結"
}
```

### POST /password-reset-confirm/
**Purpose**: Confirm password reset with token

**Request Body**:
```json
{
  "token": "abc123def456",
  "new_password": "newsecurepass123",
  "new_password_confirm": "newsecurepass123"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "密碼重設成功，請使用新密碼登入"
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "message": "密碼重設失敗",
  "errors": {
    "token": ["無效或已過期的重設連結"],
    "new_password": ["密碼必須至少8個字符，包含字母和數字"]
  }
}
```

### POST /confirm-email/
**Purpose**: Confirm email address with token

**Request Body**:
```json
{
  "token": "def789ghi012"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "電子郵件確認成功，您的帳戶現已啟用"
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "message": "電子郵件確認失敗",
  "errors": {
    "token": ["無效或已過期的確認連結"]
  }
}
```

### GET /profile/
**Purpose**: Get current user profile (requires authentication)

**Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 123,
      "email": "user@example.com",
      "first_name": "張",
      "last_name": "小明",
      "preferred_language": "zh-hant",
      "is_email_confirmed": true,
      "date_joined": "2025-01-27T10:30:00Z"
    }
  }
}
```

**Error Response (401)**:
```json
{
  "success": false,
  "message": "需要登入才能存取此資源"
}
```

## Status Codes
- `200`: Success
- `201`: Created (registration)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid credentials, not logged in)
- `429`: Too Many Requests (rate limited)
- `500`: Internal Server Error

## Rate Limiting
- Login attempts: 3 per 15 minutes per IP address
- Password reset: 5 per hour per IP address
- Registration: 10 per hour per IP address

## CSRF Protection
All state-changing operations (POST, PUT, DELETE) require CSRF token in header or form data.

## Language Support
- Request header `Accept-Language: zh-hant` for Traditional Chinese
- Request header `Accept-Language: en` for English
- Fallback to English if preferred language not available