"""
Product models for Taiwan e-commerce platform.
Includes categories, products, variants, and images with bilingual support.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Category(models.Model):
    """
    Product category with hierarchical structure and bilingual support.
    """
    name = models.CharField(
        _('分類名稱 / Category Name'),
        max_length=200,
        help_text=_('產品分類名稱（繁體中文）/ Product category name (Traditional Chinese)')
    )
    
    name_en = models.CharField(
        _('分類名稱（英文）/ Category Name (English)'),
        max_length=200,
        blank=True,
        help_text=_('英文分類名稱 / English category name')
    )
    
    slug = models.SlugField(
        _('網址代碼 / URL Slug'),
        max_length=200,
        unique=True,
        help_text=_('用於URL的唯一代碼 / Unique code for URLs')
    )
    
    description = models.TextField(
        _('描述 / Description'),
        blank=True,
        help_text=_('分類描述（繁體中文）/ Category description (Traditional Chinese)')
    )
    
    description_en = models.TextField(
        _('描述（英文）/ Description (English)'),
        blank=True,
        help_text=_('英文分類描述 / English category description')
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('上層分類 / Parent Category'),
        help_text=_('父分類（如果有）/ Parent category (if any)')
    )
    
    image = models.ImageField(
        _('分類圖片 / Category Image'),
        upload_to='categories/',
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField(
        _('啟用 / Active'),
        default=True,
        help_text=_('是否顯示此分類 / Whether to display this category')
    )
    
    display_order = models.IntegerField(
        _('顯示順序 / Display Order'),
        default=0,
        help_text=_('排序順序（數字越小越前面）/ Sort order (lower numbers appear first)')
    )
    
    # SEO fields
    meta_title = models.CharField(
        _('SEO標題 / SEO Title'),
        max_length=200,
        blank=True,
        help_text=_('搜尋引擎顯示標題（繁體中文）/ Search engine title (Traditional Chinese)')
    )
    
    meta_title_en = models.CharField(
        _('SEO標題（英文）/ SEO Title (English)'),
        max_length=200,
        blank=True,
        help_text=_('英文搜尋引擎標題 / English search engine title')
    )
    
    meta_description = models.TextField(
        _('SEO描述 / SEO Description'),
        blank=True,
        help_text=_('搜尋引擎顯示描述（繁體中文）/ Search engine description (Traditional Chinese)')
    )
    
    meta_description_en = models.TextField(
        _('SEO描述（英文）/ SEO Description (English)'),
        blank=True,
        help_text=_('英文搜尋引擎描述 / English search engine description')
    )
    
    created_at = models.DateTimeField(
        _('創建時間 / Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('產品分類 / Product Category')
        verbose_name_plural = _('產品分類 / Product Categories')
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'display_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Main product model with Taiwan-specific pricing and bilingual information.
    """
    
    STATUS_CHOICES = [
        ('draft', _('草稿 / Draft')),
        ('active', _('上架中 / Active')),
        ('out_of_stock', _('缺貨 / Out of Stock')),
        ('discontinued', _('停售 / Discontinued')),
    ]
    
    name = models.CharField(
        _('產品名稱 / Product Name'),
        max_length=300,
        help_text=_('產品名稱（繁體中文）/ Product name (Traditional Chinese)')
    )
    
    name_en = models.CharField(
        _('產品名稱（英文）/ Product Name (English)'),
        max_length=300,
        blank=True,
        help_text=_('英文產品名稱 / English product name')
    )
    
    slug = models.SlugField(
        _('網址代碼 / URL Slug'),
        max_length=300,
        unique=True,
        help_text=_('用於URL的唯一代碼 / Unique code for URLs')
    )
    
    sku = models.CharField(
        _('產品編號 / SKU'),
        max_length=100,
        unique=True,
        help_text=_('庫存單位編號 / Stock Keeping Unit')
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('分類 / Category')
    )
    
    description = models.TextField(
        _('產品描述 / Product Description'),
        help_text=_('詳細產品描述（繁體中文）/ Detailed product description (Traditional Chinese)')
    )
    
    description_en = models.TextField(
        _('產品描述（英文）/ Product Description (English)'),
        blank=True,
        help_text=_('英文產品描述 / English product description')
    )
    
    specifications = models.TextField(
        _('產品規格 / Specifications'),
        blank=True,
        help_text=_('技術規格（繁體中文）/ Technical specifications (Traditional Chinese)')
    )
    
    specifications_en = models.TextField(
        _('產品規格（英文）/ Specifications (English)'),
        blank=True,
        help_text=_('英文技術規格 / English technical specifications')
    )
    
    # Taiwan pricing in NT$ (New Taiwan Dollar)
    price = models.DecimalField(
        _('售價（新台幣）/ Price (NT$)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('新台幣售價 / Price in New Taiwan Dollar')
    )
    
    sale_price = models.DecimalField(
        _('特價（新台幣）/ Sale Price (NT$)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('促銷價格（如果有）/ Promotional price (if any)')
    )
    
    cost_price = models.DecimalField(
        _('成本價（新台幣）/ Cost Price (NT$)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('進貨成本（內部使用）/ Purchase cost (internal use)')
    )
    
    # Inventory
    stock = models.IntegerField(
        _('庫存數量 / Stock Quantity'),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('現有庫存數量 / Current stock quantity')
    )
    
    low_stock_threshold = models.IntegerField(
        _('低庫存警示 / Low Stock Threshold'),
        default=10,
        validators=[MinValueValidator(0)],
        help_text=_('低於此數量時顯示警告 / Show warning when below this quantity')
    )
    
    # Status
    status = models.CharField(
        _('狀態 / Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text=_('產品狀態 / Product status')
    )
    
    is_featured = models.BooleanField(
        _('精選產品 / Featured Product'),
        default=False,
        help_text=_('是否顯示在首頁精選區 / Display in homepage featured section')
    )
    
    is_new = models.BooleanField(
        _('新品 / New Arrival'),
        default=False,
        help_text=_('是否標示為新品 / Mark as new arrival')
    )
    
    # Product details
    weight = models.DecimalField(
        _('重量（公克）/ Weight (grams)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('產品重量（用於運費計算）/ Product weight (for shipping calculation)')
    )
    
    dimensions = models.CharField(
        _('尺寸 / Dimensions'),
        max_length=100,
        blank=True,
        help_text=_('產品尺寸（長x寬x高 cm）/ Product dimensions (L x W x H cm)')
    )
    
    # SEO
    meta_title = models.CharField(
        _('SEO標題 / SEO Title'),
        max_length=200,
        blank=True,
        help_text=_('搜尋引擎顯示標題（繁體中文）/ Search engine title (Traditional Chinese)')
    )
    
    meta_title_en = models.CharField(
        _('SEO標題（英文）/ SEO Title (English)'),
        max_length=200,
        blank=True,
        help_text=_('英文搜尋引擎標題 / English search engine title')
    )
    
    meta_description = models.TextField(
        _('SEO描述 / SEO Description'),
        blank=True,
        help_text=_('搜尋引擎顯示描述（繁體中文）/ Search engine description (Traditional Chinese)')
    )
    
    meta_description_en = models.TextField(
        _('SEO描述（英文）/ SEO Description (English)'),
        blank=True,
        help_text=_('英文搜尋引擎描述 / English search engine description')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('創建時間 / Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    published_at = models.DateTimeField(
        _('上架時間 / Published At'),
        null=True,
        blank=True,
        help_text=_('產品上架日期時間 / Product publish date and time')
    )
    
    # Statistics
    view_count = models.IntegerField(
        _('瀏覽次數 / View Count'),
        default=0,
        help_text=_('產品被瀏覽的次數 / Number of times product was viewed')
    )
    
    sales_count = models.IntegerField(
        _('銷售數量 / Sales Count'),
        default=0,
        help_text=_('已售出數量 / Number of units sold')
    )
    
    class Meta:
        verbose_name = _('產品 / Product')
        verbose_name_plural = _('產品 / Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        
        # Set published_at when status changes to active
        if self.status == 'active' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.sale_price and self.sale_price < self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.is_on_sale:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Check if stock is low."""
        return 0 < self.stock <= self.low_stock_threshold


class ProductImage(models.Model):
    """
    Product images with ordering support and bilingual alt text.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('產品 / Product')
    )
    
    image = models.ImageField(
        _('圖片 / Image'),
        upload_to='products/%Y/%m/',
        help_text=_('產品圖片 / Product image')
    )
    
    alt_text = models.CharField(
        _('替代文字 / Alt Text'),
        max_length=200,
        blank=True,
        help_text=_('圖片替代文字（繁體中文，用於SEO）/ Image alt text (Traditional Chinese, for SEO)')
    )
    
    alt_text_en = models.CharField(
        _('替代文字（英文）/ Alt Text (English)'),
        max_length=200,
        blank=True,
        help_text=_('英文圖片替代文字（用於SEO）/ English image alt text (for SEO)')
    )
    
    is_primary = models.BooleanField(
        _('主要圖片 / Primary Image'),
        default=False,
        help_text=_('是否為主要顯示圖片 / Whether this is the primary display image')
    )
    
    display_order = models.IntegerField(
        _('顯示順序 / Display Order'),
        default=0,
        help_text=_('排序順序 / Sort order')
    )
    
    created_at = models.DateTimeField(
        _('上傳時間 / Uploaded At'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('產品圖片 / Product Image')
        verbose_name_plural = _('產品圖片 / Product Images')
        ordering = ['display_order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - 圖片 {self.display_order} / Image {self.display_order}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset others
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Product variants for different options (color, size, etc) with bilingual names.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('產品 / Product')
    )
    
    name = models.CharField(
        _('規格名稱 / Variant Name'),
        max_length=200,
        help_text=_('例如：紅色/L號/256GB / e.g., Red/L/256GB')
    )
    
    name_en = models.CharField(
        _('規格名稱（英文）/ Variant Name (English)'),
        max_length=200,
        blank=True,
        help_text=_('英文規格名稱 / English variant name')
    )
    
    sku = models.CharField(
        _('規格編號 / Variant SKU'),
        max_length=100,
        unique=True,
        help_text=_('規格專屬SKU / Unique SKU for this variant')
    )
    
    price_difference = models.DecimalField(
        _('價格差異（新台幣）/ Price Difference (NT$)'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('相對於主產品的價格調整（可為負數）/ Price adjustment relative to main product (can be negative)')
    )
    
    stock = models.IntegerField(
        _('庫存數量 / Stock Quantity'),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('此規格的庫存數量 / Stock quantity for this variant')
    )
    
    is_active = models.BooleanField(
        _('啟用 / Active'),
        default=True,
        help_text=_('是否可供選擇 / Whether this variant is available for selection')
    )
    
    display_order = models.IntegerField(
        _('顯示順序 / Display Order'),
        default=0
    )
    
    created_at = models.DateTimeField(
        _('創建時間 / Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('產品規格 / Product Variant')
        verbose_name_plural = _('產品規格 / Product Variants')
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def final_price(self):
        """Calculate final price including adjustment."""
        base_price = self.product.sale_price if self.product.sale_price else self.product.price
        return base_price + self.price_difference
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock > 0

