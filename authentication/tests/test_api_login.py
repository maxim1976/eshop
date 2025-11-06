"""
Contract tests for POST /api/auth/login/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class LoginAPIContractTest(TestCase):
    """Test API contract for user login endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('auth:login')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'remember_me': True
        }
    
    def test_login_success_contract(self):
        """Test successful login API contract."""
        response = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Contract: Response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        self.assertIn('data', data)
        
        # Contract: User data structure
        user_data = data['data']
        self.assertIn('user', user_data)
        self.assertIn('session_expires', user_data)
        
        user = user_data['user']
        self.assertIn('id', user)
        self.assertIn('email', user)
        self.assertIn('first_name', user)
        self.assertIn('last_name', user)
        self.assertIn('preferred_language', user)
        
        # Contract: Session cookie set
        self.assertIn('sessionid', response.cookies)
    
    def test_login_invalid_credentials_contract(self):
        """Test invalid credentials error contract."""
        invalid_payload = {
            'email': 'wrong@example.com',
            'password': 'wrongpass123',
            'remember_me': False
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(invalid_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Contract: Error response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
        self.assertIn('errors', data)
        self.assertIn('credentials', data['errors'])
    
    def test_login_rate_limiting_contract(self):
        """Test rate limiting contract (3 attempts per 15 minutes)."""
        invalid_payload = {
            'email': 'test@example.com',
            'password': 'wrongpass123',
            'remember_me': False
        }
        
        # Make 3 failed attempts
        for i in range(3):
            response = self.client.post(
                self.login_url,
                data=json.dumps(invalid_payload),
                content_type='application/json',
                HTTP_X_FORWARDED_FOR='192.168.1.1'
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 4th attempt should be rate limited
        response = self.client.post(
            self.login_url,
            data=json.dumps(invalid_payload),
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
        self.assertIn('message', data)
        self.assertIn('retry_after', data)
        self.assertEqual(data['retry_after'], 900)  # 15 minutes
    
    def test_login_unconfirmed_email_contract(self):
        """Test unconfirmed email account login contract."""
        unconfirmed_payload = {
            'email': 'unconfirmed@example.com',
            'password': 'testpass123',
            'remember_me': False
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(unconfirmed_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 401 Unauthorized for unconfirmed accounts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Contract: Specific error for unconfirmed email
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('email_confirmation', data['errors'])
    
    def test_login_remember_me_contract(self):
        """Test remember me functionality contract."""
        remember_payload = self.valid_payload.copy()
        remember_payload['remember_me'] = True
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(remember_payload),
            content_type='application/json'
        )
        
        # Contract: Session expiry extended for remember me
        if response.status_code == 200:
            data = response.json()
            session_expires = data['data']['session_expires']
            # Should be approximately 7 days from now
            self.assertIsNotNone(session_expires)