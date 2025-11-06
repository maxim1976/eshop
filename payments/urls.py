"""
URL configuration for payments app.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Web Views
    path('initiate/<int:order_id>/', views.PaymentInitiationView.as_view(), name='initiate'),
    path('status/<str:payment_id>/', views.payment_status, name='status'),
    path('result/', views.payment_result, name='result'),
    
    # ECPay Callback
    path('ecpay/callback/', views.ecpay_callback, name='ecpay_callback'),
    
    # API Endpoints
    path('api/status/<str:payment_id>/', views.payment_status_api, name='api_status'),
    path('api/query/<str:payment_id>/', views.query_payment_api, name='api_query'),
    path('api/methods/', views.payment_methods_api, name='api_methods'),
    path('api/create/', views.create_payment_api, name='api_create'),
]