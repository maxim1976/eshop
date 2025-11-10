# Django Admin Credentials

## 🔐 Admin Access Information

### **Development Environment**

**Django Admin URL**: `http://127.0.0.1:8000/admin/`

**Superuser Credentials**:
- **Email**: `admin@日日鮮肉品專賣.com`
- **Password**: `admin123456`
- **Name**: 系統管理員 (System Administrator)
- **Language**: Traditional Chinese (zh-hant)
- **Status**: ✅ Active, ✅ Staff, ✅ Superuser, ✅ Email Confirmed

### **Admin Interface Features**

#### **🇹🇼 Traditional Chinese Interface**
- All admin labels and messages in Traditional Chinese
- Taiwan-specific date/time formatting
- Localized field names and descriptions
- Cultural appropriate admin experience

#### **User Management Dashboard**
- **CustomUser Admin**: Complete user management with Taiwan localization
  - List view: Email, Name, Language, Status, Join Date
  - Filters: Active, Staff, Superuser, Email Confirmed, Language, PDPA Consent
  - Search: By email, first name, last name
  - Bulk actions: Confirm emails, activate/deactivate users
  - Edit forms: Personal info, permissions, dates, account status, privacy

#### **Authentication Token Management**
- **EmailConfirmationToken Admin**: Monitor email confirmation process
  - View all confirmation tokens with expiration status
  - Track usage and user association
  - Manage token lifecycle
  
- **PasswordResetToken Admin**: Password reset oversight
  - Monitor reset requests and completions
  - Track token usage and expiration
  - Security audit capabilities

#### **Security Monitoring**
- **LoginAttempt Admin**: Authentication attempt tracking
  - Monitor successful/failed login attempts
  - IP address and user agent tracking
  - Bulk cleanup of old attempt records
  - Security pattern analysis

### **Admin Capabilities**

#### **User Administration**
1. **Account Management**
   - Create, edit, delete user accounts
   - Bulk activate/deactivate users
   - Manual email confirmation
   - Password reset administration

2. **Permission Management**
   - User role assignment (staff, superuser)
   - Group and permission management
   - Individual user permission control

3. **Data Management**
   - PDPA consent tracking and management
   - Language preference updates
   - User profile information editing

#### **Security Administration**
1. **Authentication Oversight**
   - Monitor login attempt patterns
   - Track failed authentication events
   - Review token usage and security

2. **System Monitoring**
   - Database content oversight
   - User activity tracking
   - System health verification

### **Quick Admin Tasks**

#### **Manual Email Confirmation**
1. Go to **Authentication** → **Custom users**
2. Find the user by email
3. Click on the user to edit
4. Check ✅ **Email confirmed** field
5. Check ✅ **Active** field (if needed)
6. Click **Save**

#### **Password Reset for User**
1. Go to **Authentication** → **Custom users**
2. Find the user by email
3. Click on the user to edit
4. Click **this form** link next to Password field
5. Enter new password and confirmation
6. Click **Change password**

#### **Bulk User Activation**
1. Go to **Authentication** → **Custom users**
2. Select users with checkboxes
3. Choose **Activate selected users** from Actions dropdown
4. Click **Go**

### **Development Usage**

#### **Starting Admin Session**
```bash
# Start Django development server
cd C:\Users\maxim\Documents\dev\copilot\ecom\日日鮮肉品專賣
set DJANGO_SETTINGS_MODULE=日日鮮肉品專賣.settings.development
python manage.py runserver

# Access admin at http://127.0.0.1:8000/admin/
# Login with admin@日日鮮肉品專賣.com / admin123456
```

#### **Admin Interface Tour**
1. **Dashboard**: Overview of all available models
2. **Authentication**: User and token management
3. **Groups**: Permission group management
4. **Sites**: Django sites framework (if needed)

### **Production Security Requirements**

⚠️ **CRITICAL**: The current credentials are for development only!

#### **Production Deployment Checklist**
1. **✅ Create New Superuser**: Use strong, unique credentials
2. **✅ Remove Development Admin**: Delete default admin account
3. **✅ Environment Variables**: Store credentials securely
4. **✅ HTTPS Only**: Secure admin access with SSL
5. **✅ IP Restrictions**: Limit admin access by IP address
6. **✅ 2FA Implementation**: Add two-factor authentication
7. **✅ Regular Audits**: Monitor admin access logs

#### **Creating Production Admin**
```bash
# On Railway.com or production server
python manage.py createsuperuser

# Use secure credentials:
# Email: your-admin@yourdomain.com
# Password: [Complex password with symbols, numbers, mixed case]
# First Name: [Your name]
# Last Name: [Your surname]
```

#### **Remove Development Admin (Production)**
```bash
python manage.py shell -c "
from authentication.models import CustomUser
try:
    dev_admin = CustomUser.objects.get(email='admin@日日鮮肉品專賣.com')
    dev_admin.delete()
    print('Development admin removed')
except CustomUser.DoesNotExist:
    print('Development admin not found')
"
```

### **Admin Security Best Practices**

#### **Access Control**
- ✅ Use strong, unique passwords (minimum 12 characters)
- ✅ Enable HTTPS for all admin access
- ✅ Implement IP address restrictions
- ✅ Regular password rotation (every 90 days)
- ✅ Monitor admin access logs
- ✅ Use separate admin accounts per administrator

#### **Operational Security**
- ✅ Log all admin actions
- ✅ Regular backup of admin configurations
- ✅ Review and audit admin permissions
- ✅ Monitor suspicious admin activities
- ✅ Implement session timeouts
- ✅ Use 2FA for sensitive operations

### **Troubleshooting Admin Issues**

#### **Cannot Access Admin**
1. **Check Server**: Ensure Django server is running
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

2. **Verify Credentials**: Test authentication in shell
   ```bash
   python manage.py shell -c "
   from django.contrib.auth import authenticate
   user = authenticate(email='admin@日日鮮肉品專賣.com', password='admin123456')
   print('Success' if user else 'Failed')
   "
   ```

3. **Check User Status**:
   ```bash
   python manage.py shell -c "
   from authentication.models import CustomUser
   user = CustomUser.objects.get(email='admin@日日鮮肉品專賣.com')
   print(f'Active: {user.is_active}, Staff: {user.is_staff}')
   "
   ```

#### **Reset Admin Password**
```bash
python manage.py changepassword admin@日日鮮肉品專賣.com
# Or via shell:
python manage.py shell -c "
from authentication.models import CustomUser
user = CustomUser.objects.get(email='admin@日日鮮肉品專賣.com')
user.set_password('new_password_here')
user.save()
print('Password updated successfully')
"
```

#### **Create Additional Admin**
```bash
python manage.py createsuperuser
# Follow prompts for email, password, and personal details
```

---

## 📊 **Admin Status Summary**

✅ **Admin User**: Created and verified  
✅ **Authentication**: Working correctly  
✅ **Admin Interface**: Traditional Chinese localization  
✅ **Security**: Development-appropriate permissions  
✅ **Models**: All authentication models registered  
✅ **Features**: Complete user and token management  

**Ready for Development Use!** 🎉

For production deployment, follow the security checklist to create secure admin credentials and remove development accounts.