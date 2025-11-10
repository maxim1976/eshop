"""
URL configuration for 日日鮮肉品專賣 project.

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
from django.http import JsonResponse
from django.shortcuts import render, redirect

def health_check(request):
    """Health check endpoint for Railway.com monitoring."""
    return JsonResponse({'status': 'healthy', 'service': '日日鮮肉品專賣'})

def accounts_login_redirect(request):
    """Redirect legacy accounts/login/ to our auth system."""
    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(f'/auth/login/?next={next_url}')
    return redirect('/auth/login/')

def home_view(request):
    """Home page view with featured products."""
    from products.models import Product
    
    # Get featured products - ordered by creation date (first entered first)  
    featured_products = Product.objects.filter(
        status='active',
        is_featured=True
    ).select_related('category').prefetch_related('images').order_by('created_at')[:6]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'home.html', context)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Health check
    path("health/", health_check, name='health-check'),
    
    # Redirect accounts/login/ to our auth system
    path("accounts/login/", accounts_login_redirect, name='accounts-login-redirect'),
    
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

# Serve media and static files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
