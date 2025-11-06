"""
Shopping cart models for Taiwan e-commerce platform.
Supports both authenticated users and guest sessions with bilingual field labels.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from products.models import Product, ProductVariant


class Cart(models.Model):
    """
    Shopping cart that works for both logged-in users and guests.
    Follows Taiwan e-commerce requirements with bilingual support.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart',
        verbose_name=_('使用者 / User'),
        help_text=_('購物車所有者（登入用戶）/ Cart owner (authenticated user)')
    )
    
    session_key = models.CharField(
        _('會話金鑰 / Session Key'),
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        help_text=_('訪客的會話標識 / Guest session identifier')
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
        verbose_name = _('購物車 / Shopping Cart')
        verbose_name_plural = _('購物車 / Shopping Carts')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        if self.user:
            return f"購物車 / Cart - {self.user.email}"
        return f"訪客購物車 / Guest Cart - {self.session_key}"
    
    def get_items_count(self):
        """
        Get total number of items in cart.
        取得購物車商品總數量
        """
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """
        Calculate cart subtotal (before shipping and tax).
        計算購物車小計（不含運費和稅金）
        """
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total(self):
        """
        Calculate cart total (can add shipping/tax here).
        計算購物車總計（可在此加入運費/稅金）
        """
        return self.get_subtotal()
    
    def clear(self):
        """
        Remove all items from cart.
        清空購物車所有商品
        """
        self.items.all().delete()
    
    def merge_with_session_cart(self, session_cart):
        """
        Merge session cart into user cart when user logs in.
        將訪客購物車合併到使用者購物車（登入時）
        
        Args:
            session_cart: Guest cart to merge from
        """
        for session_item in session_cart.items.all():
            # Check if item already exists in user cart
            # 檢查商品是否已存在於使用者購物車
            existing_item = self.items.filter(
                product=session_item.product,
                variant=session_item.variant
            ).first()
            
            if existing_item:
                # Update quantity / 更新數量
                existing_item.quantity += session_item.quantity
                existing_item.save()
            else:
                # Move item to user cart / 將商品移至使用者購物車
                session_item.cart = self
                session_item.save()
        
        # Delete session cart / 刪除訪客購物車
        session_cart.delete()


class CartItem(models.Model):
    """
    Individual item in shopping cart.
    購物車中的單一商品項目
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('購物車 / Cart')
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('產品 / Product')
    )
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('產品規格 / Product Variant'),
        help_text=_('產品變體（如有）/ Product variant (if any)')
    )
    
    quantity = models.PositiveIntegerField(
        _('數量 / Quantity'),
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_('購買數量 / Purchase quantity')
    )
    
    # Store price at time of adding to cart
    # 儲存加入購物車時的價格（用於價格變動時的歷史記錄）
    price_at_addition = models.DecimalField(
        _('加入時價格（新台幣）/ Price at Addition (NT$)'),
        max_digits=10,
        decimal_places=2,
        help_text=_('商品加入購物車時的價格 / Product price when added to cart')
    )
    
    created_at = models.DateTimeField(
        _('加入時間 / Added At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('更新時間 / Updated At'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('購物車商品 / Cart Item')
        verbose_name_plural = _('購物車商品 / Cart Items')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['-created_at']),
        ]
        # Ensure unique product/variant combination per cart
        # 確保每個購物車中產品/規格組合的唯一性
        unique_together = [['cart', 'product', 'variant']]
    
    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant.name} x {self.quantity}"
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set price_at_addition.
        覆寫儲存方法以自動設定加入時價格
        """
        # Set price if not already set / 如果尚未設定價格則自動設定
        if not self.price_at_addition:
            if self.variant and hasattr(self.variant, 'final_price') and self.variant.final_price:
                self.price_at_addition = self.variant.final_price
            elif self.product:
                # Use sale price if available, otherwise regular price
                # 如有特價則使用特價，否則使用原價
                if self.product.sale_price:
                    self.price_at_addition = self.product.sale_price
                elif self.product.price:
                    self.price_at_addition = self.product.price
                else:
                    # Fallback to 0 if no price is available
                    self.price_at_addition = 0
        super().save(*args, **kwargs)
    
    def get_price(self):
        """
        Get current price (use stored price for consistency).
        取得目前價格（使用儲存的價格以保持一致性）
        
        Returns:
            Decimal: Price per unit in NT$
        """
        if self.price_at_addition is not None:
            return self.price_at_addition
        
        # Fallback logic if price_at_addition is None
        if self.variant and hasattr(self.variant, 'final_price') and self.variant.final_price:
            return self.variant.final_price
        elif self.product:
            if self.product.sale_price:
                return self.product.sale_price
            elif self.product.price:
                return self.product.price
        
        # Last resort fallback
        return 0
    
    def get_total_price(self):
        """
        Calculate total price for this item.
        計算此商品項目的總價
        
        Returns:
            Decimal: Total price (price × quantity) in NT$
        """
        price = self.get_price()
        if price is None:
            price = 0
        return price * self.quantity
    
    def update_quantity(self, quantity):
        """
        Update item quantity or remove if quantity is 0 or less.
        更新商品數量，如果數量為 0 或更少則移除
        
        Args:
            quantity (int): New quantity
        """
        if quantity <= 0:
            self.delete()
        else:
            self.quantity = quantity
            self.save()
    
    def increase_quantity(self, amount=1):
        """
        Increase quantity by specified amount.
        增加指定數量
        
        Args:
            amount (int): Amount to increase (default: 1)
        """
        self.quantity += amount
        self.save()
    
    def decrease_quantity(self, amount=1):
        """
        Decrease quantity by specified amount or remove if result is 0 or less.
        減少指定數量，如果結果為 0 或更少則移除
        
        Args:
            amount (int): Amount to decrease (default: 1)
        """
        new_quantity = self.quantity - amount
        if new_quantity <= 0:
            self.delete()
        else:
            self.quantity = new_quantity
            self.save()
    
    @property
    def is_available(self):
        """
        Check if product/variant is still available for purchase.
        檢查產品/規格是否仍可購買
        
        Returns:
            bool: True if available, False otherwise
        """
        if self.variant:
            return self.variant.is_active and self.variant.is_in_stock
        return self.product.status == 'active' and self.product.is_in_stock
    
    @property
    def available_stock(self):
        """
        Get available stock for this item.
        取得此商品的可用庫存
        
        Returns:
            int: Available stock quantity
        """
        if self.variant:
            return self.variant.stock
        return self.product.stock
    
    @property
    def has_sufficient_stock(self):
        """
        Check if there's sufficient stock for this quantity.
        檢查庫存是否足夠供應此數量
        
        Returns:
            bool: True if sufficient stock, False otherwise
        """
        return self.available_stock >= self.quantity
    
    @property
    def stock_status(self):
        """
        Get stock status message in bilingual format.
        取得雙語庫存狀態訊息
        
        Returns:
            dict: Status information with message and level
        """
        if not self.is_available:
            return {
                'message': _('商品目前缺貨 / Product currently out of stock'),
                'level': 'error'
            }
        elif not self.has_sufficient_stock:
            return {
                'message': _('庫存不足 / Insufficient stock'),
                'level': 'warning',
                'available': self.available_stock
            }
        elif self.available_stock <= 10:
            return {
                'message': _('庫存剩餘 / Stock remaining'),
                'level': 'info',
                'available': self.available_stock
            }
        return {
            'message': _('庫存充足 / In stock'),
            'level': 'success'
        }

