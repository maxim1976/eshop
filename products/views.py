"""
Product views for browsing, searching, and viewing product details.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category


def product_list(request):
    """
    Display list of active products with filtering, search, and pagination.
    Supports Traditional Chinese and English.
    """
    # Get query parameters
    search_query = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'name')
    
    # Base queryset - only active products
    products = Product.objects.filter(status='active').select_related('category').prefetch_related('images', 'variants')
    
    # Apply search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(name_en__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(description_en__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # Apply category filter
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Apply sorting - default to first entered first (created_at ASC)
    sort_options = {
        'name': 'name',
        'name_en': 'name_en', 
        'price_low': 'price',
        'price_high': '-price',
        'newest': '-created_at',
        'oldest': 'created_at',  # First entered first
    }
    products = products.order_by(sort_options.get(sort_by, 'created_at'))  # Default to oldest first
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter sidebar
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_slug,
        'current_sort': sort_by,
        'total_products': products.count(),
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Display detailed product information including variants and images.
    """
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'variants'),
        slug=slug,
        status='active'
    )
    
    # Get related products from same category
    # Get related products in same category (first entered first)
    related_products = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(id=product.id).prefetch_related('images').order_by('created_at')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'images': product.images.all(),
        'variants': product.variants.all(),
    }
    
    return render(request, 'products/product_detail.html', context)


def category_list(request):
    """
    Display all active categories.
    """
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'products/category_list.html', context)
