# Data Model: User Registration and Authentication System

## Entities and Relationships

### CustomUser (extends Django AbstractUser)
**Purpose**: Core user entity for e-commerce customers with Taiwan localization support

**Attributes**:
- `id`: AutoField (Primary Key)
- `email`: EmailField (unique, used as username)
- `password`: CharField (hashed with Django's PBKDF2)
- `first_name`: CharField (optional)
- `last_name`: CharField (optional)
- `preferred_language`: CharField (choices: 'zh-hant', 'en', default: 'zh-hant')
- `is_email_confirmed`: BooleanField (default: False)
- `pdpa_consent`: BooleanField (default: False)
- `pdpa_consent_date`: DateTimeField (nullable)
- `date_joined`: DateTimeField (auto_now_add)
- `last_login`: DateTimeField (nullable)
- `is_active`: BooleanField (default: False, activated after email confirmation)

**Relationships**:
- One-to-Many: User → AuthenticationSession
- One-to-Many: User → PasswordResetToken
- One-to-Many: User → EmailConfirmationToken

**Indexes**:
- email (unique)
- is_active, is_email_confirmed (compound)

### AuthenticationSession (extends Django Session)
**Purpose**: Track user sessions with remember me functionality

**Attributes**:
- `session_key`: CharField (Primary Key, Django default)
- `user`: ForeignKey to CustomUser (nullable for anonymous)
- `created_at`: DateTimeField (auto_now_add)
- `expires_at`: DateTimeField (7 days default, or browser close)
- `remember_me`: BooleanField (default: False)
- `ip_address`: GenericIPAddressField
- `user_agent`: TextField

**Relationships**:
- Many-to-One: AuthenticationSession → CustomUser

**Indexes**:
- user_id, expires_at (compound)
- session_key (unique, Django default)

### EmailConfirmationToken
**Purpose**: Temporary tokens for email verification (48-hour expiration)

**Attributes**:
- `id`: AutoField (Primary Key)
- `user`: ForeignKey to CustomUser
- `token`: CharField (UUID4, unique)
- `email`: EmailField (the email being confirmed)
- `created_at`: DateTimeField (auto_now_add)
- `expires_at`: DateTimeField (created_at + 48 hours)
- `is_used`: BooleanField (default: False)

**Relationships**:
- Many-to-One: EmailConfirmationToken → CustomUser

**Indexes**:
- token (unique)
- user_id, is_used (compound)
- expires_at (for cleanup jobs)

### PasswordResetToken
**Purpose**: Temporary tokens for password reset requests (4-hour expiration)

**Attributes**:
- `id`: AutoField (Primary Key)
- `user`: ForeignKey to CustomUser
- `token`: CharField (UUID4, unique)
- `created_at`: DateTimeField (auto_now_add)
- `expires_at`: DateTimeField (created_at + 4 hours)
- `is_used`: BooleanField (default: False)
- `ip_address`: GenericIPAddressField (requesting IP)

**Relationships**:
- Many-to-One: PasswordResetToken → CustomUser

**Indexes**:
- token (unique)
- user_id, is_used (compound)
- expires_at (for cleanup jobs)

### LoginAttempt
**Purpose**: Track failed login attempts for rate limiting (3 per 15 minutes)

**Attributes**:
- `id`: AutoField (Primary Key)
- `email`: EmailField (attempted email)
- `ip_address`: GenericIPAddressField
- `attempted_at`: DateTimeField (auto_now_add)
- `success`: BooleanField
- `user_agent`: TextField

**Relationships**:
- None (denormalized for performance)

**Indexes**:
- email, attempted_at (compound)
- ip_address, attempted_at (compound)
- attempted_at (for cleanup jobs)

### UserPreferences
**Purpose**: Store user preferences and settings

**Attributes**:
- `id`: AutoField (Primary Key)
- `user`: OneToOneField to CustomUser
- `language`: CharField (choices: 'zh-hant', 'en', default: 'zh-hant')
- `timezone`: CharField (default: 'Asia/Taipei')
- `email_notifications`: BooleanField (default: True)
- `marketing_emails`: BooleanField (default: False)
- `created_at`: DateTimeField (auto_now_add)
- `updated_at`: DateTimeField (auto_now)

**Relationships**:
- One-to-One: UserPreferences → CustomUser

## Database Constraints

### Data Integrity
- Email uniqueness enforced at database level
- Password reset/email confirmation tokens expire automatically
- PDPA consent required before account activation
- Session cleanup job runs daily to remove expired sessions

### Performance Optimizations
- Compound indexes for common query patterns
- Token cleanup jobs to prevent table bloat
- Connection pooling for Railway PostgreSQL
- Query optimization for authentication flows

### Security Constraints
- Passwords hashed with PBKDF2 (Django default)
- Tokens use cryptographically secure UUIDs
- IP address logging for security auditing
- Session data encrypted in database

## Migration Strategy

### Initial Migration
1. Create CustomUser model (extends AbstractUser)
2. Create authentication-related tables
3. Set up indexes and constraints
4. Configure Django settings for custom user model

### Data Seeding
- Create superuser account for admin access
- Set up default language preferences
- Configure email templates in both languages

### Railway Deployment
- Database migrations run automatically on deployment
- Environment variables for database connection
- Backup strategy for user data protection