# EShop - Taiwan E-Commerce Platform

![EShop Logo](media/pictures/logo-2-cs6ol-03.png)

## 🛍️ Overview

EShop is a comprehensive e-commerce platform designed specifically for the Taiwan market, featuring Traditional Chinese localization, PDPA compliance, and modern web technologies.

## ✨ Features

### 🔐 **Authentication System**
- Email-based user registration and login
- Email confirmation with 48-hour token expiry
- Password reset with 4-hour security tokens
- Rate limiting (3 attempts per 15 minutes)
- PDPA (Personal Data Protection Act) compliance
- Traditional Chinese / English bilingual support

### 🛒 **Shopping Experience**
- **Product Management**: Categories, variants, images, stock tracking
- **Smart Cart System**: 
  - Works for both logged-in users and guests
  - Automatic cart merging when guests login
  - Price protection (locked at add-to-cart time)
  - Real-time stock validation
- **Advanced Search & Filtering**: Category, price range, availability filters
- **Responsive Design**: Mobile-first approach with Tailwind CSS

### 💳 **Payment Integration**
- ECPay payment gateway integration (Taiwan market leader)
- Multiple payment methods (Credit Card, ATM, Convenience Store)
- Secure payment processing with callback handling
- Order tracking and status management

### 🎨 **Modern Frontend**
- Professional logo integration with responsive design
- Tailwind CSS 3.x for rapid development
- Component-based template system
- AJAX cart operations with smooth UX
- Mobile-optimized interface

## 🏗️ Technology Stack

### **Backend**
- **Framework**: Django 4.2.24
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Custom user model with email-based auth
- **Internationalization**: Django i18n with Traditional Chinese support

### **Frontend**
- **CSS Framework**: Tailwind CSS 3.x
- **JavaScript**: Vanilla JS with progressive enhancement
- **Templates**: Django template system with component architecture
- **Fonts**: Noto Sans TC for optimal Chinese character display

### **Payment & Integration**
- **Payment Gateway**: ECPay (綠界科技)
- **Email**: Django email backend (configurable for SMTP)
- **File Storage**: Django media files system
- **Session Management**: Database-backed sessions

### **Development & Deployment**
- **Package Management**: pip with requirements.txt
- **Frontend Build**: Tailwind CSS compilation
- **Deployment**: Railway.com ready with Procfile
- **Environment**: python-decouple for configuration management

## 🚀 Quick Start

### **Prerequisites**
```bash
Python 3.8+
Node.js (for Tailwind CSS compilation)
```

### **Installation**
```bash
# Clone the repository
git clone https://github.com/maxim1976/eshop.git
cd eshop

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Tailwind)
npm install

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### **Environment Configuration**
```env
# Basic Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@eshop.com

# ECPay Configuration (Taiwan Payment Gateway)
ECPAY_MERCHANT_ID=your-merchant-id
ECPAY_HASH_KEY=your-hash-key
ECPAY_HASH_IV=your-hash-iv
ECPAY_SANDBOX=True

# Site URL
SITE_URL=http://localhost:8000
```

## 📱 Usage

### **Admin Interface**
Access the admin panel at `/admin/` to manage:
- Products and categories
- User accounts and permissions
- Orders and payments
- System configuration

### **User Features**
- **Registration**: `/auth/register/` - Create new account with email confirmation
- **Login**: `/auth/login/` - Email-based authentication
- **Shopping**: `/products/` - Browse and search products
- **Cart**: `/cart/` - Manage shopping cart
- **Checkout**: `/orders/checkout/` - Complete purchase process

### **API Endpoints**
```
Authentication:
POST /api/auth/register/     - User registration
POST /api/auth/login/        - User login
POST /api/auth/logout/       - User logout
GET  /api/auth/profile/      - User profile

Shopping:
GET  /api/products/          - Product listings
POST /api/cart/add/          - Add to cart
GET  /api/cart/              - View cart

Payments:
POST /api/payments/create/   - Create payment
GET  /api/payments/status/   - Payment status
```

## 🏛️ Architecture

### **Project Structure**
```
eshop/
├── authentication/          # User management system
├── products/               # Product catalog
├── cart/                   # Shopping cart functionality
├── orders/                 # Order processing
├── payments/               # Payment gateway integration
├── templates/              # HTML templates
│   ├── components/         # Reusable UI components
│   ├── authentication/     # Auth-related templates
│   └── ...
├── static/                 # Static assets (CSS, JS, images)
├── media/                  # User-uploaded files
└── eshop/                  # Django project settings
```

### **Key Components**
- **CustomUser Model**: Email-based authentication with PDPA compliance
- **Cart System**: Dual-mode (user/guest) with automatic merging
- **Payment Service**: ECPay integration with callback handling
- **Component Templates**: Reusable UI elements (logo, pagination, etc.)

## 🔒 Security Features

### **Authentication Security**
- CSRF protection on all forms
- Rate limiting on login attempts
- Secure session management
- Password strength requirements
- Email confirmation flow

### **Data Protection**
- PDPA compliance for Taiwan market
- Secure token generation (UUID4)
- IP address tracking for security
- User consent management
- Data retention policies

### **Payment Security**
- ECPay certified integration
- Secure callback validation
- Payment status verification
- Transaction logging
- Error handling and recovery

## 🌍 Internationalization

The platform supports:
- **Traditional Chinese (zh-hant)**: Primary language
- **English (en)**: Secondary language
- **Localized UI**: All interface elements translated
- **Currency**: Taiwan Dollar (TWD) formatting
- **Time Zone**: Asia/Taipei

## 🛠️ Development

### **Contributing**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Code Standards**
- **Python**: Follow PEP 8 guidelines
- **Django**: Use Django best practices
- **Frontend**: Component-based architecture
- **Templates**: Semantic HTML with accessibility
- **JavaScript**: ES6+ with progressive enhancement

### **Testing**
```bash
# Run tests
python manage.py test

# Run with coverage
coverage run manage.py test
coverage report
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support, email support@eshop.com or create an issue in the GitHub repository.

## 🎯 Roadmap

### **Upcoming Features**
- [ ] Advanced analytics dashboard
- [ ] Multi-vendor marketplace support
- [ ] Mobile app (React Native)
- [ ] Advanced SEO optimization
- [ ] Social media integration
- [ ] Inventory management system
- [ ] Customer loyalty program

---

**Built with ❤️ for the Taiwan market** 🇹🇼