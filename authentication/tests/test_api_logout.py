"""
Contract tests for POST /api/auth/logout/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class LogoutAPIContractTest(TestCase):
    """Test API contract for user logout endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('auth:logout')
    
    def test_logout_success_contract(self):
        """Test successful logout API contract."""
        # First login to establish session
        login_url = reverse('auth:login')
        login_payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'remember_me': False
        }
        
        login_response = self.client.post(
            login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Now logout
        response = self.client.post(
            self.logout_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Contract: Response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        
        # Contract: Session cookie cleared
        sessionid_cookie = response.cookies.get('sessionid')
        if sessionid_cookie:
            # Cookie should be expired/cleared
            self.assertEqual(sessionid_cookie.value, '')
    
    def test_logout_without_session_contract(self):
        """Test logout without active session contract."""
        response = self.client.post(
            self.logout_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Still returns 200 OK (idempotent)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Contract: Success message even without session
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_logout_csrf_protection_contract(self):
        """Test logout CSRF protection contract."""
        # Login first
        login_url = reverse('auth:login')
        login_payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        self.client.post(
            login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Attempt logout without CSRF token
        response = self.client.post(
            self.logout_url,
            HTTP_X_CSRFTOKEN='invalid-token'
        )
        
        # Contract: CSRF protection active for state-changing operations
        self.assertIn(response.status_code, [403, 401])  # CSRF failure
    
    def test_logout_get_method_not_allowed_contract(self):
        """Test that GET method is not allowed for logout."""
        response = self.client.get(self.logout_url)
        
        # Contract: Only POST method allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)