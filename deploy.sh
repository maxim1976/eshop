#!/bin/bash
# Production Deployment Script for Railway.com - 日日鮮肉品專賣

echo "🏪 日日鮮肉品專賣 - Production Deployment"
echo "========================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in to Railway
echo "🔐 Checking Railway authentication..."
railway whoami || {
    echo "🔑 Please login to Railway:"
    railway login
}

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set DATABASE_URL="postgresql://postgres:GTXmeZStEhDuOPTsqlljirnfwXwSuWIA@postgres.railway.internal:5432/railway"
railway variables set DJANGO_SETTINGS_MODULE="eshop.settings.production"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="*.railway.app,localhost"

# Generate a secure secret key
echo "🔑 Setting secure secret key..."
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
railway variables set SECRET_KEY="$SECRET_KEY"

# Run migrations
echo "🗄️ Running database migrations..."
railway run python manage.py migrate

# Create superuser
echo "👤 Setting up admin account..."
railway run python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@ririshenmeat.com').exists():
    User.objects.create_superuser('admin@ririshenmeat.com', 'admin123')
    print('Superuser created: admin@ririshenmeat.com')
else:
    print('Superuser already exists')
"

# Collect static files
echo "📦 Collecting static files..."
railway run python manage.py collectstatic --noinput

# Deploy the application
echo "🚀 Deploying application..."
railway up

echo "✅ Deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Visit your Railway dashboard to get the app URL"
echo "2. Test the application functionality"
echo "3. Access admin at: [your-url]/admin/"
echo "   Username: admin@ririshenmeat.com"
echo "   Password: admin123"
echo ""
echo "🏪 Your 日日鮮肉品專賣 store is now live!"