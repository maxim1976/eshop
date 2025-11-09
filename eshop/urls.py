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

def database_status(request):
    """Database status check for debugging Railway issues."""
    try:
        from django.db import connection
        from products.models import Product, Category
        
        status = {
            'database_connected': False,
            'tables_exist': False,
            'products_count': 0,
            'categories_count': 0,
            'migrations_applied': False,
            'errors': []
        }
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            status['database_connected'] = True
        except Exception as e:
            status['errors'].append(f"Database connection failed: {str(e)}")
        
        # Test table existence and data
        if status['database_connected']:
            try:
                status['products_count'] = Product.objects.count()
                status['categories_count'] = Category.objects.count()
                status['tables_exist'] = True
            except Exception as e:
                status['errors'].append(f"Table access failed: {str(e)}")
        
        # Check migrations status
        try:
            from django.core.management import execute_from_command_line
            from django.db import DEFAULT_DB_ALIAS
            from django.db.migrations.executor import MigrationExecutor
            
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            status['migrations_applied'] = len(plan) == 0
            if plan:
                status['errors'].append(f"Unapplied migrations: {len(plan)}")
                status['pending_migrations'] = [str(migration) for migration, backwards in plan]
        except Exception as e:
            status['errors'].append(f"Migration check failed: {str(e)}")
        
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Database status check failed',
            'details': str(e)
        }, status=500)

def home_view(request):
    """Home page view with featured products and categories."""
    try:
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
    
    except Exception as e:
        # Return a simple error page for debugging
        import traceback
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'debug': os.environ.get('DEBUG', 'False')
        }
        
        if os.environ.get('DEBUG', 'False').lower() == 'true':
            # In debug mode, show full error
            return JsonResponse(error_details, status=500)
        else:
            # In production, log the error and show a simple message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Home view error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a simple HTML error page
            return HttpResponse(f"""
                <html>
                <head><title>Service Temporarily Unavailable</title></head>
                <body>
                    <h1>Service Temporarily Unavailable</h1>
                    <p>We're experiencing technical difficulties. Please try again later.</p>
                    <p>Error: {str(e)}</p>
                </body>
                </html>
            """, status=500)

urlpatterns = [
    # Simple health checks - put these first
    path("ping/", simple_health, name='simple-health'),
    path("health/", database_status, name='database-status'),
    path("status/", database_status, name='health-check'),  # Keep old endpoint working
    
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
