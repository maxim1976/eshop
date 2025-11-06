"""
Contract tests for POST /api/auth/password-reset/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class PasswordResetAPIContractTest(TestCase):
    """Test API contract for password reset request endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.password_reset_url = reverse('auth:password-reset')
    
    def test_password_reset_success_contract(self):
        """Test successful password reset request API contract."""
        payload = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Always returns 200 OK for security (don't reveal if email exists)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Contract: Response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        
        # Contract: Generic security message
        message = data['message']
        self.assertIn('如果該電子郵件存在於我們的系統中', message)
    
    def test_password_reset_nonexistent_email_contract(self):
        """Test password reset for nonexistent email contract."""
        payload = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Same response for security (don't reveal email doesn't exist)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Contract: Same message structure
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_password_reset_invalid_email_format_contract(self):
        """Test password reset with invalid email format contract."""
        payload = {
            'email': 'invalid-email-format'
        }
        
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request for invalid format
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Validation error structure
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
    
    def test_password_reset_rate_limiting_contract(self):
        """Test password reset rate limiting contract (5 per hour per IP)."""
        payload = {
            'email': 'test@example.com'
        }
        
        # Make 5 requests
        for i in range(5):
            response = self.client.post(
                self.password_reset_url,
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_X_FORWARDED_FOR='192.168.1.1'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6th request should be rate limited
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_FORWARDED_FOR='192.168.1.1',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 429 Too Many Requests
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Contract: Rate limit response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('retry_after', data)
        self.assertEqual(data['retry_after'], 3600)  # 1 hour
    
    def test_password_reset_missing_email_contract(self):
        """Test password reset without email field contract."""
        payload = {}
        
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Required field error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
    
    def test_password_reset_csrf_protection_contract(self):
        """Test password reset CSRF protection contract."""
        payload = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(
            self.password_reset_url,
            data=payload,
            HTTP_X_CSRFTOKEN='invalid-token'
        )
        
        # Contract: CSRF protection active
        self.assertIn(response.status_code, [403, 401])  # CSRF failure