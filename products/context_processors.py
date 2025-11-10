from .models import Category


def category_nav_context(request):
    """
    Provide a lightweight list of active top-level categories for global navigation.
    Returns categories ordered by display_order then name with fields used in templates.
    """
    try:
        categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('display_order', 'name')
    except Exception:
        categories = Category.objects.none()
    return {
        'nav_categories': categories,
    }
