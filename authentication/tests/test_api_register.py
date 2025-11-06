"""
Contract tests for POST /api/auth/register/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class RegisterAPIContractTest(TestCase):
    """Test API contract for user registration endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth:register')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': '張',
            'last_name': '小明',
            'preferred_language': 'zh-hant',
            'pdpa_consent': True
        }
    
    def test_register_success_contract(self):
        """Test successful registration API contract."""
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Contract: Response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        self.assertIn('data', data)
        
        # Contract: Data structure
        user_data = data['data']
        self.assertIn('user_id', user_data)
        self.assertIn('email', user_data)
        self.assertIn('confirmation_sent', user_data)
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertTrue(user_data['confirmation_sent'])
    
    def test_register_duplicate_email_contract(self):
        """Test duplicate email error contract."""
        # First registration should succeed
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        # Second registration with same email should fail
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Error response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
    
    def test_register_invalid_password_contract(self):
        """Test password validation error contract."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['password'] = '123'  # Too short, no letters
        invalid_payload['password_confirm'] = '123'
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Password error in Traditional Chinese
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('password', data['errors'])
    
    def test_register_missing_pdpa_consent_contract(self):
        """Test PDPA consent requirement contract."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['pdpa_consent'] = False
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: PDPA consent error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('pdpa_consent', data['errors'])
    
    def test_register_csrf_protection_contract(self):
        """Test CSRF protection contract."""
        # Without CSRF token, should be rejected
        response = self.client.post(
            self.register_url,
            data=self.valid_payload,
            HTTP_X_CSRFTOKEN='invalid-token'
        )
        
        # Contract: CSRF protection active
        self.assertIn(response.status_code, [403, 401])  # CSRF failure