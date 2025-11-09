"""
URL configuration for eshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import os

def simple_health(request):
    """Ultra simple health check."""
    return HttpResponse("OK", content_type="text/plain")

def health_check(request):
    """Simple health check endpoint for Railway.com monitoring."""
    try:
        # Just return a simple response without database checks
        return JsonResponse({
            'status': 'healthy', 
            'service': 'eshop',
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
            'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown'),
            'allowed_hosts': getattr(settings, 'ALLOWED_HOSTS', [])
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy', 
            'error': str(e)
        }, status=500)

def home_view(request):
    """Home page view with featured products and categories."""
    from products.models import Product, Category
    
    # Get featured products
    featured_products = Product.objects.filter(
        status='active',
        is_featured=True
    ).select_related('category').prefetch_related('images')[:6]
    
    # Get categories for display
    categories = Category.objects.filter(
        is_active=True
    ).order_by('display_order', 'name')[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)

urlpatterns = [
    # Simple health checks - put these first
    path("ping/", simple_health, name='simple-health'),
    path("health/", health_check, name='health-check'),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # Home
    path("", home_view, name='home'),
    
    # Authentication
    path("", include('authentication.urls')),
    
    # Products
    path("products/", include('products.urls')),
    
    # Cart
    path("cart/", include('cart.urls')),
    
    # Orders
    path("orders/", include('orders.urls')),
    
    # Payments  
    path("payments/", include('payments.urls')),
    
    # Internationalization (language switching)
    path("i18n/", include('django.conf.urls.i18n')),
]

# Serve media files in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
