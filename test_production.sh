#!/bin/bash
# Quick Production Test Script for 日日鮮肉品專賣

echo "🧪 Testing Production Deployment..."

# Configuration
DOMAIN="your-app-name.railway.app"  # Replace with your actual Railway domain
HTTPS_URL="https://${DOMAIN}"

echo "🌐 Testing: ${HTTPS_URL}"

# Test 1: Basic connectivity
echo "1️⃣ Testing basic connectivity..."
if curl -f -s -o /dev/null "${HTTPS_URL}"; then
    echo "✅ Site is reachable"
else
    echo "❌ Site is not reachable"
    exit 1
fi

# Test 2: Health check endpoint
echo "2️⃣ Testing health check..."
HEALTH_RESPONSE=$(curl -s "${HTTPS_URL}/health/")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed: $HEALTH_RESPONSE"
fi

# Test 3: Admin interface
echo "3️⃣ Testing admin interface..."
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${HTTPS_URL}/admin/")
if [ "$ADMIN_STATUS" = "302" ] || [ "$ADMIN_STATUS" = "200" ]; then
    echo "✅ Admin interface accessible"
else
    echo "❌ Admin interface error: HTTP $ADMIN_STATUS"
fi

# Test 4: Static files
echo "4️⃣ Testing static files..."
STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${HTTPS_URL}/static/css/")
if [ "$STATIC_STATUS" != "404" ]; then
    echo "✅ Static files configured"
else
    echo "⚠️ Static files may not be properly configured"
fi

# Test 5: HTTPS enforcement
echo "5️⃣ Testing HTTPS enforcement..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${DOMAIN}")
if [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo "✅ HTTPS redirect working"
else
    echo "⚠️ HTTPS redirect may not be configured"
fi

# Test 6: Database connectivity (via health endpoint)
echo "6️⃣ Testing database connectivity..."
if echo "$HEALTH_RESPONSE" | grep -q "connected"; then
    echo "✅ Database connected"
else
    echo "❌ Database connection issues"
fi

echo ""
echo "🎯 Production Test Summary:"
echo "- Update DOMAIN variable in this script with your Railway domain"
echo "- All tests should pass before going live"
echo "- Monitor Railway logs during first few hours"
echo ""
echo "📊 Next Steps:"
echo "1. Create admin superuser: railway shell -> python manage.py createsuperuser"
echo "2. Test payment with small amount (NT$1)"
echo "3. Verify email notifications are working"
echo "4. Test mobile experience"
echo ""
echo "🚀 Ready to launch 日日鮮肉品專賣!"