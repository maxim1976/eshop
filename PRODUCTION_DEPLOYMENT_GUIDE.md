# 🚀 Production Deployment Guide - 日日鮮肉品專賣

## 📋 **Pre-Deployment Checklist**

### ✅ **1. Code Quality & Security**
- [ ] All tests passing
- [ ] Admin interface working (✅ Already fixed)
- [ ] No DEBUG=True in production
- [ ] SECRET_KEY properly configured
- [ ] No hardcoded credentials in code
- [ ] CSRF protection enabled
- [ ] Rate limiting configured

### ✅ **2. Database & Media**
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Media files storage configured
- [ ] Backup strategy implemented
- [ ] Database indexes optimized

### ✅ **3. Environment Configuration**
- [ ] Environment variables set
- [ ] Railway.com PostgreSQL configured
- [ ] Email service configured
- [ ] SSL/TLS certificates ready
- [ ] Domain name configured

---

## 🔧 **Step 1: Prepare Production Files**

### **Update WSGI Configuration**
```python
# eshop/wsgi.py - Update for production
import os
from django.core.wsgi import get_wsgi_application

# Use production settings on Railway
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eshop.settings.production")

application = get_wsgi_application()
```

### **Environment Variables for Railway.com**
```bash
# Required Environment Variables
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,yourdomain.com
DATABASE_URL=postgresql://... # Auto-provided by Railway
DJANGO_SETTINGS_MODULE=eshop.settings.production

# Email Configuration (SendGrid recommended)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# ECPay Production (IMPORTANT!)
ECPAY_MERCHANT_ID=your-production-merchant-id
ECPAY_HASH_KEY=your-production-hash-key
ECPAY_HASH_IV=your-production-hash-iv
ECPAY_SANDBOX=False

# Site Configuration
SITE_URL=https://your-domain.railway.app
CORS_ALLOWED_ORIGINS=https://your-domain.railway.app,https://yourdomain.com

# Taiwan Specific
LANGUAGE_CODE=zh-hant
TIME_ZONE=Asia/Taipei
```

---

## 🚄 **Step 2: Railway.com Deployment**

### **A. Prepare Repository**
```bash
# 1. Commit all changes
git add .
git commit -m "🚀 Prepare for production deployment"

# 2. Create production branch (optional)
git checkout -b production
```

### **B. Deploy to Railway**
```bash
# Option 1: Railway CLI (Recommended)
npm install -g @railway/cli
railway login
railway link  # Connect to your Railway project
railway up    # Deploy

# Option 2: GitHub Integration
# - Connect Railway to your GitHub repository
# - Configure auto-deploy from main/production branch
```

### **C. Configure Services**
```bash
# 1. Add PostgreSQL Database
railway add postgresql

# 2. Configure Environment Variables in Railway Dashboard
# - Navigate to your project settings
# - Add all environment variables listed above

# 3. Configure Custom Domain (Optional)
# - Add your domain in Railway settings
# - Configure DNS CNAME record
```

---

## ⚡ **Step 3: Database Setup**

### **A. Run Migrations**
```bash
# Railway automatically runs migrations via Procfile
# Manual trigger if needed:
railway shell
python manage.py migrate
python manage.py collectstatic --noinput
```

### **B. Create Superuser**
```bash
# Via Railway shell
railway shell
python manage.py createsuperuser

# Enter admin details for 日日鮮肉品專賣
Email: admin@日日鮮肉品專賣.com
Password: [secure password]
```

### **C. Load Initial Data (Optional)**
```bash
# If you have fixtures or sample data
python manage.py loaddata initial_categories.json
python manage.py loaddata sample_products.json
```

---

## 🔐 **Step 4: Security Configuration**

### **A. SSL/HTTPS Setup**
Railway provides automatic SSL. Verify:
- [ ] HTTPS redirects working
- [ ] SSL certificate valid
- [ ] Security headers enabled

### **B. Payment Gateway (ECPay) Setup**
```python
# CRITICAL: Update to PRODUCTION ECPay credentials
ECPAY_SANDBOX=False  # MUST be False for production
ECPAY_MERCHANT_ID=your_real_merchant_id
ECPAY_HASH_KEY=your_production_hash_key
ECPAY_HASH_IV=your_production_hash_iv
```

### **C. Security Monitoring**
- [ ] Enable Railway monitoring
- [ ] Set up error notifications
- [ ] Configure log monitoring
- [ ] Enable security alerts

---

## 📧 **Step 5: Email Service Setup**

### **Option A: SendGrid (Recommended for Taiwan)**
```bash
# 1. Create SendGrid account
# 2. Get API key
# 3. Configure DNS records
# 4. Set environment variables:
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

### **Option B: Gmail SMTP**
```bash
# For smaller operations
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-business-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

---

## 🌐 **Step 6: Domain & DNS Setup**

### **A. Custom Domain (Optional)**
```bash
# 1. Purchase domain (recommended .tw for Taiwan)
# 2. Configure DNS in Railway:
#    CNAME: www -> your-app.railway.app
#    A: @ -> Railway IP
# 3. Update ALLOWED_HOSTS
```

### **B. CDN Setup (Optional)**
```bash
# For better Taiwan performance
# 1. Configure Cloudflare
# 2. Enable Taiwan optimization
# 3. Set up proper caching rules
```

---

## 📊 **Step 7: Monitoring & Maintenance**

### **A. Health Checks**
```python
# Already configured in railway.json
"healthcheckPath": "/health/"
```

### **B. Backup Strategy**
```bash
# Database backups (Railway provides automatic backups)
# For additional security:
railway backup create
```

### **C. Performance Monitoring**
- [ ] Railway metrics enabled
- [ ] Database performance monitoring
- [ ] Error tracking configured
- [ ] User analytics setup

---

## 🧪 **Step 8: Testing Production**

### **A. Functionality Tests**
- [ ] User registration/login working
- [ ] Product browsing working
- [ ] Shopping cart functional
- [ ] Payment flow complete (TEST with small amount!)
- [ ] Email notifications sending
- [ ] Admin interface accessible
- [ ] Mobile responsiveness verified

### **B. Performance Tests**
- [ ] Page load times < 3 seconds
- [ ] Database queries optimized
- [ ] Static files loading properly
- [ ] Image optimization working

### **C. Security Tests**
- [ ] HTTPS enforcement working
- [ ] Rate limiting functional
- [ ] CSRF protection enabled
- [ ] SQL injection protection
- [ ] XSS protection enabled

---

## 🎯 **Step 9: Go Live Process**

### **A. Soft Launch**
1. Deploy to production
2. Test with limited users
3. Monitor for 24-48 hours
4. Fix any issues found

### **B. Full Launch**
1. Announce on social media
2. Enable all marketing
3. Monitor closely for first week
4. Scale resources as needed

### **C. Post-Launch**
1. Daily monitoring for first month
2. Weekly performance reviews
3. Monthly security updates
4. Quarterly feature additions

---

## 🆘 **Emergency Procedures**

### **A. Rollback Plan**
```bash
# Quick rollback if issues found
railway rollback
# Or deploy previous version
git checkout previous-working-commit
railway up
```

### **B. Emergency Contacts**
- Railway Support: support@railway.app
- ECPay Support: [Taiwan payment support]
- Domain Provider: [Your domain provider]
- Developer: [Your contact info]

---

## 💰 **Cost Optimization**

### **Railway.com Pricing (Est.)**
- **Starter Plan**: $5/month + usage
- **PostgreSQL**: $5/month
- **Total**: ~$10-15/month initially

### **Taiwan Payment Processing**
- **ECPay Fees**: ~2.8-3.5% per transaction
- **Bank Fees**: Additional 1-2%

### **Scaling Considerations**
- Start with basic plan
- Monitor usage metrics
- Scale based on actual traffic
- Optimize database queries

---

## ✅ **Launch Checklist**

### **Technical**
- [ ] Production environment deployed
- [ ] Database migrated and tested
- [ ] Payment gateway tested (small amount)
- [ ] Email notifications working
- [ ] SSL certificate active
- [ ] Domain configured
- [ ] Monitoring enabled

### **Business**
- [ ] Content reviewed and approved
- [ ] Product catalog complete
- [ ] Pricing verified
- [ ] Terms of service published
- [ ] Privacy policy compliant (PDPA)
- [ ] Customer support ready

### **Legal (Taiwan)**
- [ ] Business registration complete
- [ ] Tax ID configured
- [ ] PDPA compliance verified
- [ ] Consumer protection compliance
- [ ] Food safety certifications

---

## 🎉 **Ready for Launch!**

Your **日日鮮肉品專賣** is now ready for production deployment! 

**Next Steps:**
1. Follow this guide step by step
2. Test thoroughly in production environment
3. Launch with soft opening
4. Monitor and optimize continuously

**Success Metrics to Track:**
- User registrations
- Order completion rates  
- Payment success rates
- Page load times
- Error rates
- Customer satisfaction

Good luck with your Taiwan meat specialty store launch! 🥩🚀