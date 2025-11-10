# Authentication 404 Error - FIXED!

## ❌ **Problem Identified**

Django was redirecting unauthenticated users to `/accounts/login/` but your authentication URLs are at `/auth/login/`.

### **Error Details:**
```
Page not found (404)
Request Method: GET
Request URL: http://127.0.0.1:8000/accounts/login/?next=/orders/checkout/
```

### **Root Cause:**
Django's `@login_required` decorator uses the `LOGIN_URL` setting to redirect unauthenticated users. By default, Django uses `/accounts/login/`, but your app uses `/auth/login/`.

## ✅ **Solution Applied**

### **1. Added Missing Django Settings**
Updated `eshop/settings/base.py`:
```python
# Custom User Model
AUTH_USER_MODEL = 'authentication.CustomUser'

# Authentication URLs (NEW)
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Authentication Backends
```

### **2. Settings Explained**
- **`LOGIN_URL`**: Where to redirect unauthenticated users
- **`LOGIN_REDIRECT_URL`**: Where to go after successful login (default)
- **`LOGOUT_REDIRECT_URL`**: Where to go after logout

## 🔄 **How It Works Now**

### **Before (Broken):**
1. User visits `/orders/checkout/` without login
2. Django redirects to `/accounts/login/?next=/orders/checkout/`
3. ❌ **404 Error** - URL doesn't exist

### **After (Fixed):**
1. User visits `/orders/checkout/` without login
2. Django redirects to `/auth/login/?next=/orders/checkout/`
3. ✅ **Login form appears**
4. After login → redirects back to `/orders/checkout/`

## 📋 **Authentication Flow**

### **Your URL Structure:**
```
/auth/login/           ← Login form
/auth/register/        ← Registration form  
/auth/logout/          ← Logout action
/auth/profile/         ← User profile
/orders/checkout/      ← Protected checkout page
```

### **Protected Pages:**
Any page decorated with `@login_required` will now correctly redirect to `/auth/login/` instead of causing 404 errors.

## ✅ **Verification**

### **Test the Fix:**
1. **Visit Checkout**: http://127.0.0.1:8000/orders/checkout/
2. **Expected**: Redirects to login form (not 404)
3. **URL Should Be**: `/auth/login/?next=/orders/checkout/`
4. **After Login**: Returns to checkout page

### **Other Protected Pages:**
- User profile
- Order history  
- Admin sections
- Any view with `@login_required`

## 🎯 **Result**

Your **日日鮮肉品專賣** authentication flow is now working correctly:

- ✅ **No more 404 errors** for unauthenticated users
- ✅ **Smooth checkout flow** with login redirect
- ✅ **Proper user experience** - login then continue shopping
- ✅ **Consistent authentication** across all protected pages

## 🔧 **Technical Details**

### **Django Authentication Settings:**
```python
# Tells Django where to send unauthenticated users
LOGIN_URL = '/auth/login/'

# Default redirect after login (can be overridden by 'next' parameter)
LOGIN_REDIRECT_URL = '/'

# Where to go after logout
LOGOUT_REDIRECT_URL = '/'
```

### **URL Patterns That Work:**
- `/auth/login/` ✅
- `/auth/register/` ✅
- `/auth/logout/` ✅
- `/orders/checkout/` ✅ (with proper redirect)

---
**Issue**: 404 error on authentication redirect  
**Cause**: Missing LOGIN_URL setting  
**Solution**: Set LOGIN_URL = '/auth/login/'  
**Status**: ✅ **RESOLVED**

Your meat store authentication is now seamless! 🥩🔐