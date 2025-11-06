from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout process / 結帳流程
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    
    # Order management / 訂單管理
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),
]