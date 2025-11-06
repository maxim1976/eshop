"""
Payment views for Taiwan e-commerce platform with ECPay integration.
Handles payment initiation, callbacks, and status queries.
"""

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.translation import gettext as _
from django.contrib import messages
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit

from orders.models import Order
from .models import Payment, PaymentLog
from .services import PaymentService
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)


class PaymentInitiationView(View):
    """
    Handle payment initiation for orders.
    Creates payment record and redirects to ECPay.
    """
    
    @method_decorator(login_required)
    @method_decorator(ratelimit(key='user', rate='10/5m', method='POST'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, order_id):
        """Display payment selection page."""
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order can be paid
        if order.payment_status != 'pending':
            messages.error(request, _('此訂單無法付款 / This order cannot be paid'))
            return redirect('orders:order_detail', order_id=order.id)
        
        # Get payment methods
        payment_service = PaymentService()
        payment_methods = payment_service.ecpay.get_payment_methods_config()
        
        context = {
            'order': order,
            'payment_methods': payment_methods,
        }
        
        return render(request, 'payments/payment_selection.html', context)
    
    def post(self, request, order_id):
        """Process payment initiation."""
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order can be paid
        if order.payment_status != 'pending':
            messages.error(request, _('此訂單無法付款 / This order cannot be paid'))
            return redirect('orders:order_detail', order_id=order.id)
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            messages.warning(request, _('此訂單已有付款記錄 / Payment already exists for this order'))
            return redirect('payments:status', payment_id=order.payment.payment_id)
        
        # Get payment method
        payment_method = request.POST.get('payment_method', 'Credit')
        
        # Create payment
        payment_service = PaymentService()
        result = payment_service.create_payment(
            order=order,
            payment_method=payment_method,
            client_back_url=request.build_absolute_uri(reverse('orders:order_detail', args=[order.id])),
            order_result_url=request.build_absolute_uri(reverse('payments:result')),
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        if result['success']:
            # Render ECPay form submission page
            context = {
                'form_data': result['form_data'],
                'action_url': result['action_url'],
                'payment': result['payment'],
                'order': order,
            }
            return render(request, 'payments/ecpay_redirect.html', context)
        else:
            messages.error(request, _('付款建立失敗，請稍後再試 / Payment creation failed, please try again'))
            return redirect('orders:order_detail', order_id=order.id)
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@csrf_exempt
@require_POST
def ecpay_callback(request):
    """
    Handle ECPay payment callback.
    This endpoint receives POST data from ECPay when payment is completed.
    """
    try:
        # Get callback data
        callback_data = request.POST.dict()
        
        logger.info(f"ECPay callback received: {callback_data}")
        
        # Process callback
        payment_service = PaymentService()
        result = payment_service.handle_callback(
            callback_data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        if result['success']:
            logger.info(f"Payment callback processed successfully: {result['merchant_trade_no']}")
            return HttpResponse('1|OK')  # ECPay expects '1|OK' for successful processing
        else:
            logger.error(f"Payment callback processing failed: {result}")
            return HttpResponse('0|Failed')
            
    except Exception as e:
        logger.error(f"ECPay callback error: {str(e)}")
        return HttpResponse('0|Error')


@login_required
def payment_status(request, payment_id):
    """
    Display payment status page.
    Shows current payment status and details.
    """
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    
    return render(request, 'payments/payment_status.html', context)


@login_required
def payment_result(request):
    """
    Payment result page after returning from ECPay.
    """
    # Get the latest payment for this user
    try:
        payment = Payment.objects.filter(user=request.user).latest('created_at')
        context = {
            'payment': payment,
            'order': payment.order,
        }
        return render(request, 'payments/payment_result.html', context)
    except Payment.DoesNotExist:
        messages.error(request, _('找不到付款記錄 / No payment record found'))
        return redirect('orders:order_list')


# API Views for AJAX requests

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/1m', method='GET')
def payment_status_api(request, payment_id):
    """
    API endpoint to check payment status.
    Used for AJAX polling on payment status page.
    """
    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='5/1m', method='POST')
def query_payment_api(request, payment_id):
    """
    API endpoint to query payment status from ECPay.
    Forces a fresh check with ECPay servers.
    """
    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        
        payment_service = PaymentService()
        result = payment_service.query_payment_status(payment_id)
        
        if result:
            return Response({
                'success': True,
                'data': result
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to query payment status'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_methods_api(request):
    """
    API endpoint to get available payment methods.
    """
    payment_service = PaymentService()
    payment_methods = payment_service.ecpay.get_payment_methods_config()
    
    return Response({
        'success': True,
        'payment_methods': payment_methods
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/5m', method='POST')
def create_payment_api(request):
    """
    API endpoint to create payment for an order.
    """
    try:
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'Credit')
        
        if not order_id:
            return Response(
                {'error': 'Order ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order can be paid
        if order.payment_status != 'pending':
            return Response(
                {'error': 'This order cannot be paid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Payment already exists for this order'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment
        payment_service = PaymentService()
        result = payment_service.create_payment(
            order=order,
            payment_method=payment_method,
            client_back_url=request.build_absolute_uri(reverse('orders:order_detail', args=[order.id])),
            order_result_url=request.build_absolute_uri(reverse('payments:result')),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        if result['success']:
            return Response({
                'success': True,
                'payment_id': result['payment'].payment_id,
                'form_data': result['form_data'],
                'action_url': result['action_url'],
                'method': result['method']
            })
        else:
            return Response(
                {'error': 'Payment creation failed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Payment creation API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
