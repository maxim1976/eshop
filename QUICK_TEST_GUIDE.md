# Quick Test Guide - Web Forms

## 🚀 Start Testing Now!

Your server is already running at: **http://127.0.0.1:8000/**

---

## ✅ Test #1: Visit Home Page

**Action**: Open http://127.0.0.1:8000/

**Expected**:
- Beautiful home page with blue hero section
- "立即註冊" and "登入" buttons
- Features section showing 安全可靠, 快速便捷, 優質服務
- Footer with links

---

## ✅ Test #2: Register New Account

**Action**: Click "立即註冊" or visit http://127.0.0.1:8000/auth/register/

**Fill in form**:
```
電子郵件地址: demo@example.com
名字: 示範
姓氏: 用戶
密碼: demopass123
確認密碼: demopass123
偏好語言: 繁體中文
✅ 我同意個人資料保護法條款
```

**Click**: 註冊

**Expected**:
- Redirect to login page
- Green success message: "註冊成功！請檢查您的電子郵件以確認帳戶。"
- Check your terminal/console for email with confirmation link

---

## ✅ Test #3: Confirm Email

**Action**: Look at your terminal output for email

You'll see something like:
```
電子郵件地址: demo@example.com
請點擊以下連結確認您的電子郵件地址:
http://127.0.0.1:8000/auth/confirm-email/?token=abc123...
```

**Action**: Copy the URL and visit it in browser

**Expected**:
- "電子郵件確認成功！您的帳戶現已啟用，可以登入了。"
- Link to login page

---

## ✅ Test #4: Login

**Action**: Visit http://127.0.0.1:8000/auth/login/

**Fill in**:
```
電子郵件地址: demo@example.com
密碼: demopass123
✅ 記住我（7天）
```

**Click**: 登入

**Expected**:
- Redirect to profile page
- Green success message: "登入成功！歡迎回來。"
- Header now shows your name with dropdown menu

---

## ✅ Test #5: View Profile

**Expected** (already on profile page):
- See your account information
- Email confirmation status: ✅
- PDPA consent status: ✅
- Can edit name and language preference

**Try**: Update your name and click save

**Expected**:
- Green message: "個人資料已更新。"

---

## ✅ Test #6: Navigation

**Action**: Click on your name in the header

**Expected**: Dropdown menu with:
- 個人資料
- 訂單記錄
- 設定
- 登出

---

## ✅ Test #7: Logout

**Action**: Click "登出" from dropdown

**Expected**:
- Redirect to login page
- Message: "已成功登出。"
- Header now shows "登入" and "註冊" buttons

---

## ✅ Test #8: Password Reset

**Action**: Visit http://127.0.0.1:8000/auth/password-reset/

**Fill in**:
```
電子郵件地址: demo@example.com
```

**Click**: Submit

**Expected**:
- Redirect to login page
- Message: "如果該電子郵件存在於我們的系統中，您將收到重設密碼的連結。"
- Check terminal for reset email with link

**Action**: Copy reset link from terminal and visit it

**Fill in new password**:
```
新密碼: newdemo456
確認新密碼: newdemo456
```

**Click**: Submit

**Expected**:
- Redirect to login
- Message: "密碼重設成功！請使用新密碼登入。"

**Action**: Login with new password

**Expected**: Should work!

---

## ✅ Test #9: Error Handling

### Try Login Without Confirmation

**Action**: Register a new user but DON'T click the confirmation link

**Then**: Try to login

**Expected**: Error message "請先確認您的電子郵件地址才能登入"

### Try Wrong Password

**Action**: Login with correct email but wrong password

**Expected**: "電子郵件或密碼錯誤"

### Try Duplicate Email

**Action**: Register with an email that already exists

**Expected**: "此電子郵件地址已被使用"

### Try Weak Password

**Action**: Register with password "weak"

**Expected**: Password validation error

---

## 🎯 All Tests Passed?

If all tests above work correctly, you have a **fully functional authentication system**! 🎉

### What You've Verified:
✅ Registration with email confirmation  
✅ Email sending and token validation  
✅ Login with session management  
✅ Profile viewing and editing  
✅ Password reset flow  
✅ Logout functionality  
✅ Error handling and validation  
✅ Messages and user feedback  
✅ Navigation and UI elements  

---

## 🐛 Troubleshooting

### Server Not Running?
```powershell
python manage.py runserver --settings=eshop.settings.development
```

### Can't See Emails?
Check your terminal/console output - emails are printed there in development mode.

### Token Expired?
Confirmation tokens expire after 48 hours, reset tokens after 4 hours. Register/reset again to get new tokens.

### Page Not Loading?
Make sure you're using the correct URL with `/auth/` prefix for web forms.

### Form Styling Broken?
We're using Tailwind CSS. The basic styling should work, but full compilation can be done later.

---

## 📝 Quick URLs Reference

```
Home:         http://127.0.0.1:8000/
Register:     http://127.0.0.1:8000/auth/register/
Login:        http://127.0.0.1:8000/auth/login/
Profile:      http://127.0.0.1:8000/auth/profile/
Reset:        http://127.0.0.1:8000/auth/password-reset/
Admin:        http://127.0.0.1:8000/admin/
Health:       http://127.0.0.1:8000/health/
```

---

**Happy Testing!** 🚀

Your Taiwan e-commerce authentication system is ready to use!
