/**
 * EShop Cart Management JavaScript
 * Handles AJAX cart operations and UI updates
 */

class CartManager {
  constructor() {
    this.cartCountBadge = document.querySelector('.cart-count-badge');
    this.addToCartForms = document.querySelectorAll('.add-to-cart-form');
    this.wishlistButtons = document.querySelectorAll('.wishlist-btn');
    this.init();
  }
  
  init() {
    // Add to cart functionality
    this.addToCartForms.forEach(form => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.addToCart(form);
      });
    });
    
    // Wishlist functionality (placeholder)
    this.wishlistButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.toggleWishlist(button);
      });
    });
    
    // Update cart count on page load
    this.updateCartCount();
    
    // Cart item management (if on cart page)
    this.initCartItemControls();
  }
  
  async addToCart(form) {
    const formData = new FormData(form);
    const button = form.querySelector('button[type="submit"]');
    const originalText = button.textContent;
    
    // Show loading state
    button.textContent = '加入中...';
    button.disabled = true;
    button.classList.add('opacity-50');
    
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCSRFToken(),
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Update cart count
        this.updateCartCount();
        
        // Show success feedback
        this.showNotification(data.message || '商品已加入購物車', 'success');
        
        // Animate button
        button.textContent = '已加入 ✓';
        button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        button.classList.add('bg-green-600');
        
        setTimeout(() => {
          button.textContent = originalText;
          button.classList.remove('bg-green-600');
          button.classList.add('bg-blue-600', 'hover:bg-blue-700');
        }, 2000);
      } else {
        this.showNotification(data.message || '加入購物車失敗', 'error');
      }
    } catch (error) {
      console.error('Add to cart error:', error);
      this.showNotification('網路錯誤，請重試', 'error');
    } finally {
      button.disabled = false;
      button.classList.remove('opacity-50');
      if (button.textContent === '加入中...') {
        button.textContent = originalText;
      }
    }
  }
  
  async updateCartCount() {
    try {
      const response = await fetch('/cart/count/', {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      const data = await response.json();
      
      if (this.cartCountBadge && data.count !== undefined) {
        this.cartCountBadge.textContent = data.count;
        this.cartCountBadge.style.display = data.count > 0 ? 'flex' : 'none';
        
        // Animate the badge
        this.cartCountBadge.classList.add('animate-pulse');
        setTimeout(() => {
          this.cartCountBadge.classList.remove('animate-pulse');
        }, 1000);
      }
    } catch (error) {
      console.error('Update cart count error:', error);
    }
  }
  
  async toggleWishlist(button) {
    const productId = button.dataset.productId;
    const icon = button.querySelector('svg');
    
    // Toggle visual state immediately for better UX
    const isAdded = button.classList.contains('text-red-500');
    
    if (isAdded) {
      button.classList.remove('text-red-500');
      button.classList.add('text-gray-600');
      icon.setAttribute('fill', 'none');
    } else {
      button.classList.remove('text-gray-600');
      button.classList.add('text-red-500');
      icon.setAttribute('fill', 'currentColor');
    }
    
    try {
      const response = await fetch('/wishlist/toggle/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken(),
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ product_id: productId })
      });
      
      const data = await response.json();
      
      if (data.success) {
        this.showNotification(
          data.added ? '已加入收藏清單' : '已從收藏清單移除', 
          'success'
        );
      } else {
        // Revert visual state if request failed
        if (isAdded) {
          button.classList.remove('text-gray-600');
          button.classList.add('text-red-500');
          icon.setAttribute('fill', 'currentColor');
        } else {
          button.classList.remove('text-red-500');
          button.classList.add('text-gray-600');
          icon.setAttribute('fill', 'none');
        }
        this.showNotification(data.message || '操作失敗', 'error');
      }
    } catch (error) {
      console.error('Wishlist toggle error:', error);
      // Revert visual state on error
      if (isAdded) {
        button.classList.remove('text-gray-600');
        button.classList.add('text-red-500');
        icon.setAttribute('fill', 'currentColor');
      } else {
        button.classList.remove('text-red-500');
        button.classList.add('text-gray-600');
        icon.setAttribute('fill', 'none');
      }
      this.showNotification('網路錯誤，請重試', 'error');
    }
  }
  
  initCartItemControls() {
    // Quantity update controls
    document.querySelectorAll('.quantity-btn').forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.updateQuantity(button);
      });
    });
    
    // Remove item buttons
    document.querySelectorAll('.remove-item-btn').forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.removeItem(button);
      });
    });
    
    // Quantity input direct change
    document.querySelectorAll('.quantity-input').forEach(input => {
      input.addEventListener('change', (e) => {
        this.updateQuantityDirect(e.target);
      });
    });
  }
  
  async updateQuantity(button) {
    const action = button.dataset.action;
    const itemId = button.dataset.itemId;
    const quantityInput = button.parentNode.querySelector('.quantity-input');
    const currentQuantity = parseInt(quantityInput.value);
    
    let newQuantity;
    if (action === 'increase') {
      newQuantity = currentQuantity + 1;
    } else if (action === 'decrease') {
      newQuantity = Math.max(1, currentQuantity - 1);
    }
    
    await this.updateCartItem(itemId, newQuantity, quantityInput);
  }
  
  async updateQuantityDirect(input) {
    const itemId = input.dataset.itemId;
    const newQuantity = Math.max(1, parseInt(input.value) || 1);
    
    await this.updateCartItem(itemId, newQuantity, input);
  }
  
  async updateCartItem(itemId, quantity, quantityInput) {
    try {
      const response = await fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken(),
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ quantity: quantity })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Update quantity input
        quantityInput.value = quantity;
        
        // Update item total
        const itemRow = quantityInput.closest('.cart-item');
        const totalElement = itemRow.querySelector('.item-total');
        if (totalElement) {
          totalElement.textContent = `NT$ ${data.item_total}`;
        }
        
        // Update cart totals
        this.updateCartTotals(data.cart_total);
        this.updateCartCount();
        
        this.showNotification('購物車已更新', 'success');
      } else {
        this.showNotification(data.message || '更新失敗', 'error');
      }
    } catch (error) {
      console.error('Update cart item error:', error);
      this.showNotification('網路錯誤，請重試', 'error');
    }
  }
  
  async removeItem(button) {
    const itemId = button.dataset.itemId;
    const itemRow = button.closest('.cart-item');
    
    // Show confirmation
    if (!confirm('確定要移除此商品嗎？')) {
      return;
    }
    
    try {
      const response = await fetch(`/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.getCSRFToken(),
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Animate item removal
        itemRow.style.transition = 'all 0.3s ease';
        itemRow.style.transform = 'translateX(100%)';
        itemRow.style.opacity = '0';
        
        setTimeout(() => {
          itemRow.remove();
          
          // Check if cart is empty
          const remainingItems = document.querySelectorAll('.cart-item');
          if (remainingItems.length === 0) {
            window.location.reload(); // Reload to show empty cart state
          }
        }, 300);
        
        // Update cart totals
        this.updateCartTotals(data.cart_total);
        this.updateCartCount();
        
        this.showNotification('商品已從購物車移除', 'success');
      } else {
        this.showNotification(data.message || '移除失敗', 'error');
      }
    } catch (error) {
      console.error('Remove cart item error:', error);
      this.showNotification('網路錯誤，請重試', 'error');
    }
  }
  
  updateCartTotals(cartTotal) {
    const totalElements = document.querySelectorAll('.cart-total');
    totalElements.forEach(element => {
      element.textContent = `NT$ ${cartTotal}`;
    });
  }
  
  showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.cart-notification').forEach(n => n.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `cart-notification fixed top-4 right-4 z-50 px-4 py-3 rounded-md shadow-lg text-white max-w-sm transform transition-transform duration-300 ${
      type === 'success' ? 'bg-green-500' : 
      type === 'error' ? 'bg-red-500' : 
      'bg-blue-500'
    }`;
    notification.innerHTML = `
      <div class="flex items-center">
        <span class="flex-1">${message}</span>
        <button class="ml-2 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 4000);
  }
  
  getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new CartManager();
});

// Export for use in other scripts
window.CartManager = CartManager;