"""
Contract tests for POST /api/auth/password-reset-confirm/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class PasswordResetConfirmAPIContractTest(TestCase):
    """Test API contract for password reset confirmation endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.password_confirm_url = reverse('auth:password-reset-confirm')
        self.valid_payload = {
            'token': 'valid-reset-token-123',
            'new_password': 'newsecurepass123',
            'new_password_confirm': 'newsecurepass123'
        }
    
    def test_password_reset_confirm_success_contract(self):
        """Test successful password reset confirmation API contract."""
        response = self.client.post(
            self.password_confirm_url,
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
        
        # Contract: Success message in Traditional Chinese
        message = data['message']
        self.assertIn('密碼重設成功', message)
    
    def test_password_reset_confirm_invalid_token_contract(self):
        """Test invalid token error contract."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['token'] = 'invalid-token-123'
        
        response = self.client.post(
            self.password_confirm_url,
            data=json.dumps(invalid_payload),
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
        self.assertIn('token', data['errors'])
    
    def test_password_reset_confirm_expired_token_contract(self):
        """Test expired token error contract (4 hour expiration)."""
        expired_payload = self.valid_payload.copy()
        expired_payload['token'] = 'expired-token-123'
        
        response = self.client.post(
            self.password_confirm_url,
            data=json.dumps(expired_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Expired token error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('token', data['errors'])
        # Should mention expiration in error message
        error_message = str(data['errors']['token'])
        self.assertIn('已過期', error_message)
    
    def test_password_reset_confirm_weak_password_contract(self):
        """Test weak password validation contract."""
        weak_payload = self.valid_payload.copy()
        weak_payload['new_password'] = '123'  # Too short, no letters
        weak_payload['new_password_confirm'] = '123'
        
        response = self.client.post(
            self.password_confirm_url,
            data=json.dumps(weak_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Password validation errors
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('new_password', data['errors'])
    
    def test_password_reset_confirm_password_mismatch_contract(self):
        """Test password confirmation mismatch contract."""
        mismatch_payload = self.valid_payload.copy()
        mismatch_payload['new_password'] = 'newsecurepass123'
        mismatch_payload['new_password_confirm'] = 'differentsecurepass123'
        
        response = self.client.post(
            self.password_confirm_url,
            data=json.dumps(mismatch_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Password mismatch error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('new_password_confirm', data['errors'])
    
    def test_password_reset_confirm_used_token_contract(self):
        """Test already used token contract."""
        used_payload = self.valid_payload.copy()
        used_payload['token'] = 'used-token-123'
        
        response = self.client.post(
            self.password_confirm_url,
            data=json.dumps(used_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Used token error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('token', data['errors'])
    
    def test_password_reset_confirm_missing_fields_contract(self):
        """Test missing required fields contract."""
        incomplete_payload = {
            'token': 'valid-token-123'
            # Missing new_password and new_password_confirm
        }
        
        response = self.client.post(
            self.password_confirm_url,
            data=json.dumps(incomplete_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Required field errors
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('new_password', data['errors'])
        self.assertIn('new_password_confirm', data['errors'])