"""
Product admin interface with bilingual support and Taiwan-specific features.
Follows Django best practices and EShop coding standards.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Category, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'alt_text_en', 'is_primary', 'display_order')
    readonly_fields = ('created_at',)


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""
    model = ProductVariant
    extra = 0
    fields = ('name', 'name_en', 'sku', 'price_difference', 'stock', 'is_active', 'display_order')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for product categories with bilingual support."""
    
    list_display = (
        'name_display',
        'parent',
        'product_count',
        'is_active',
        'display_order',
        'updated_at'
    )
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'name_en', 'description', 'description_en')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('基本資訊 / Basic Information'), {
            'fields': ('name', 'name_en', 'slug', 'parent')
        }),
        (_('描述 / Description'), {
            'fields': ('description', 'description_en')
        }),
        (_('顯示設定 / Display Settings'), {
            'fields': ('image', 'is_active', 'display_order')
        }),
        (_('SEO 設定 / SEO Settings'), {
            'fields': (
                'meta_title',
                'meta_title_en',
                'meta_description',
                'meta_description_en'
            ),
            'classes': ('collapse',)
        }),
        (_('系統資訊 / System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name_display(self, obj):
        """Display category name in both languages."""
        return format_html(
            '<strong>{}</strong><br/><span style="color: #6b7280; font-size: 0.875rem;">{}</span>',
            obj.name,
            obj.name_en or '-'
        )
    name_display.short_description = _('分類名稱 / Category Name')
    
    def product_count(self, obj):
        """Display number of products in category."""
        count = obj.products.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    product_count.short_description = _('產品數量 / Products')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for products with Taiwan-specific features and bilingual support."""
    
    list_display = (
        'thumbnail_display',
        'name_display',
        'sku',
        'category',
        'price_display',
        'stock_display',
        'status_display',
        'is_featured',
        'updated_at'
    )
    list_filter = (
        'status',
        'is_featured',
        'is_new',
        'category',
        'created_at'
    )
    search_fields = ('name', 'name_en', 'sku', 'description', 'description_en')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = (
        'created_at',
        'updated_at',
        'published_at',
        'view_count',
        'sales_count',
        'primary_image_preview'
    )
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (_('基本資訊 / Basic Information'), {
            'fields': (
                'name',
                'name_en',
                'slug',
                'sku',
                'category',
                'status'
            )
        }),
        (_('描述 / Description'), {
            'fields': (
                'description',
                'description_en',
                'specifications',
                'specifications_en'
            )
        }),
        (_('價格設定（新台幣）/ Pricing (NT$)'), {
            'fields': (
                'price',
                'sale_price',
                'cost_price'
            ),
            'description': _('所有價格以新台幣 (NT$) 為單位 / All prices in New Taiwan Dollar (NT$)')
        }),
        (_('庫存管理 / Inventory Management'), {
            'fields': (
                'stock',
                'low_stock_threshold'
            )
        }),
        (_('產品特性 / Product Features'), {
            'fields': (
                'is_featured',
                'is_new',
                'weight',
                'dimensions'
            )
        }),
        (_('SEO 設定 / SEO Settings'), {
            'fields': (
                'meta_title',
                'meta_title_en',
                'meta_description',
                'meta_description_en'
            ),
            'classes': ('collapse',)
        }),
        (_('統計資訊 / Statistics'), {
            'fields': (
                'view_count',
                'sales_count',
                'created_at',
                'updated_at',
                'published_at'
            ),
            'classes': ('collapse',)
        }),
        (_('主圖預覽 / Primary Image Preview'), {
            'fields': ('primary_image_preview',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_active', 'mark_as_featured', 'mark_as_out_of_stock']
    
    def thumbnail_display(self, obj):
        """Display product thumbnail."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                primary_image.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #e5e7eb; border-radius: 4px;"></div>')
    thumbnail_display.short_description = _('圖片 / Image')
    
    def name_display(self, obj):
        """Display product name in both languages."""
        return format_html(
            '<strong>{}</strong><br/><span style="color: #6b7280; font-size: 0.875rem;">{}</span>',
            obj.name,
            obj.name_en or '-'
        )
    name_display.short_description = _('產品名稱 / Product Name')
    
    def price_display(self, obj):
        """Display price with sale price if applicable."""
        if obj.sale_price and obj.sale_price < obj.price:
            discount_pct = obj.discount_percentage
            return format_html(
                '<div style="line-height: 1.5;">'
                '<span style="text-decoration: line-through; color: #9ca3af;">NT$ {}</span><br/>'
                '<span style="font-weight: bold; color: #dc2626;">NT$ {}</span> '
                '<span style="background: #dc2626; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75rem;">-{}%</span>'
                '</div>',
                f"{obj.price:,.0f}",
                f"{obj.sale_price:,.0f}",
                discount_pct
            )
        return format_html(
            '<span style="font-weight: bold;">NT$ {}</span>',
            f"{obj.price:,.0f}"
        )
    price_display.short_description = _('價格 / Price')
    
    def stock_display(self, obj):
        """Display stock with color coding."""
        if obj.stock == 0:
            color = '#dc2626'
            icon = '❌'
            text = _('缺貨 / Out of Stock')
        elif obj.is_low_stock:
            color = '#f59e0b'
            icon = '⚠️'
            text = f'{obj.stock} ({_("低庫存 / Low Stock")})'
        else:
            color = '#059669'
            icon = '✓'
            text = f'{obj.stock}'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            text
        )
    stock_display.short_description = _('庫存 / Stock')
    
    def status_display(self, obj):
        """Display status with color coding."""
        status_colors = {
            'draft': '#6b7280',
            'active': '#059669',
            'out_of_stock': '#dc2626',
            'discontinued': '#4b5563',
        }
        status_labels = {
            'draft': _('草稿 / Draft'),
            'active': _('上架中 / Active'),
            'out_of_stock': _('缺貨 / Out of Stock'),
            'discontinued': _('停售 / Discontinued'),
        }
        
        color = status_colors.get(obj.status, '#6b7280')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.875rem;">{}</span>',
            color,
            label
        )
    status_display.short_description = _('狀態 / Status')
    
    def primary_image_preview(self, obj):
        """Display primary image preview in detail view."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" />',
                primary_image.image.url
            )
        return _('無主圖片 / No primary image')
    primary_image_preview.short_description = _('主圖片預覽 / Primary Image Preview')
    
    # Admin actions
    def mark_as_active(self, request, queryset):
        """Mark products as active."""
        updated = queryset.update(status='active')
        self.message_user(
            request,
            _(f'{updated} 個產品已設為上架中 / {updated} products marked as active')
        )
    mark_as_active.short_description = _('設為上架中 / Mark as Active')
    
    def mark_as_featured(self, request, queryset):
        """Mark products as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            _(f'{updated} 個產品已設為精選 / {updated} products marked as featured')
        )
    mark_as_featured.short_description = _('設為精選產品 / Mark as Featured')
    
    def mark_as_out_of_stock(self, request, queryset):
        """Mark products as out of stock."""
        updated = queryset.update(status='out_of_stock', stock=0)
        self.message_user(
            request,
            _(f'{updated} 個產品已設為缺貨 / {updated} products marked as out of stock')
        )
    mark_as_out_of_stock.short_description = _('設為缺貨 / Mark as Out of Stock')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin interface for product images."""
    
    list_display = (
        'image_preview',
        'product',
        'alt_text_display',
        'is_primary',
        'display_order',
        'created_at'
    )
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'product__name_en', 'alt_text', 'alt_text_en')
    readonly_fields = ('created_at', 'image_preview_large')
    
    fieldsets = (
        (_('圖片資訊 / Image Information'), {
            'fields': (
                'product',
                'image',
                'image_preview_large',
                'alt_text',
                'alt_text_en',
                'is_primary',
                'display_order'
            )
        }),
        (_('系統資訊 / System Information'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Display small image preview."""
        return format_html(
            '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />',
            obj.image.url
        )
    image_preview.short_description = _('預覽 / Preview')
    
    def image_preview_large(self, obj):
        """Display large image preview in detail view."""
        return format_html(
            '<img src="{}" style="max-width: 500px; max-height: 500px; border-radius: 8px;" />',
            obj.image.url
        )
    image_preview_large.short_description = _('圖片預覽 / Image Preview')
    
    def alt_text_display(self, obj):
        """Display alt text in both languages."""
        return format_html(
            '{}<br/><span style="color: #6b7280; font-size: 0.875rem;">{}</span>',
            obj.alt_text or '-',
            obj.alt_text_en or '-'
        )
    alt_text_display.short_description = _('替代文字 / Alt Text')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin interface for product variants."""
    
    list_display = (
        'variant_display',
        'product',
        'sku',
        'price_difference_display',
        'stock_display',
        'is_active',
        'updated_at'
    )
    list_filter = ('is_active', 'product__category')
    search_fields = ('name', 'name_en', 'sku', 'product__name', 'product__name_en')
    readonly_fields = ('created_at', 'updated_at', 'final_price_display')
    
    fieldsets = (
        (_('規格資訊 / Variant Information'), {
            'fields': (
                'product',
                'name',
                'name_en',
                'sku',
                'is_active',
                'display_order'
            )
        }),
        (_('價格與庫存 / Pricing & Inventory'), {
            'fields': (
                'price_difference',
                'final_price_display',
                'stock'
            )
        }),
        (_('系統資訊 / System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def variant_display(self, obj):
        """Display variant name in both languages."""
        return format_html(
            '<strong>{}</strong><br/><span style="color: #6b7280; font-size: 0.875rem;">{}</span>',
            obj.name,
            obj.name_en or '-'
        )
    variant_display.short_description = _('規格名稱 / Variant Name')
    
    def price_difference_display(self, obj):
        """Display price difference with proper formatting."""
        if obj.price_difference > 0:
            return format_html(
                '<span style="color: #dc2626;">+NT$ {}</span>',
                f"{obj.price_difference:,.0f}"
            )
        elif obj.price_difference < 0:
            return format_html(
                '<span style="color: #059669;">-NT$ {}</span>',
                f"{abs(obj.price_difference):,.0f}"
            )
        return format_html('<span style="color: #6b7280;">NT$ 0</span>')
    price_difference_display.short_description = _('價格調整 / Price Adjustment')
    
    def stock_display(self, obj):
        """Display stock with color coding."""
        if obj.stock == 0:
            return format_html(
                '<span style="color: #dc2626; font-weight: bold;">0 ({})</span>',
                _('缺貨 / Out of Stock')
            )
        elif obj.stock < 10:
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">{} ({})</span>',
                obj.stock,
                _('低庫存 / Low Stock')
            )
        return format_html(
            '<span style="color: #059669; font-weight: bold;">{}</span>',
            obj.stock
        )
    stock_display.short_description = _('庫存 / Stock')
    
    def final_price_display(self, obj):
        """Display calculated final price."""
        final_price = obj.final_price
        base_price = obj.product.sale_price if obj.product.sale_price else obj.product.price
        
        return format_html(
            '<div style="line-height: 1.5;">'
            '<span style="color: #6b7280;">基礎價格 / Base: NT$ {}</span><br/>'
            '<span style="color: #059669; font-weight: bold;">最終價格 / Final: NT$ {}</span>'
            '</div>',
            f"{base_price:,.0f}",
            f"{final_price:,.0f}"
        )
    final_price_display.short_description = _('最終價格 / Final Price')