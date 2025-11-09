"""
Context processors for products app.
Makes categories and other product-related data available globally in templates.
"""
from .models import Category


def categories_context(request):
    """
    Add active categories to template context globally.
    Used for navigation menu rendering.
    """
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')
    
    return {
        'global_categories': categories,
    }
