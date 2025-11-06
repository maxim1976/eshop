"""
Contract tests for POST /api/auth/confirm-email/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class EmailConfirmAPIContractTest(TestCase):
    """Test API contract for email confirmation endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.email_confirm_url = reverse('auth:confirm-email')
        self.valid_payload = {
            'token': 'valid-email-token-123'
        }
    
    def test_email_confirm_success_contract(self):
        """Test successful email confirmation API contract."""
        response = self.client.post(
            self.email_confirm_url,
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
        self.assertIn('電子郵件確認成功', message)
        self.assertIn('帳戶現已啟用', message)
    
    def test_email_confirm_invalid_token_contract(self):
        """Test invalid token error contract."""
        invalid_payload = {
            'token': 'invalid-email-token-123'
        }
        
        response = self.client.post(
            self.email_confirm_url,
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
    
    def test_email_confirm_expired_token_contract(self):
        """Test expired token error contract (48 hour expiration)."""
        expired_payload = {
            'token': 'expired-email-token-123'
        }
        
        response = self.client.post(
            self.email_confirm_url,
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
    
    def test_email_confirm_already_confirmed_contract(self):
        """Test already confirmed email contract."""
        confirmed_payload = {
            'token': 'already-used-token-123'
        }
        
        response = self.client.post(
            self.email_confirm_url,
            data=json.dumps(confirmed_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request or 200 OK (idempotent)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])
        
        # Contract: Appropriate message
        data = response.json()
        if response.status_code == 400:
            self.assertIn('errors', data)
            self.assertIn('token', data['errors'])
        else:
            # If idempotent, should still indicate success
            self.assertTrue(data['success'])
    
    def test_email_confirm_missing_token_contract(self):
        """Test missing token field contract."""
        empty_payload = {}
        
        response = self.client.post(
            self.email_confirm_url,
            data=json.dumps(empty_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Required field error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('token', data['errors'])
    
    def test_email_confirm_empty_token_contract(self):
        """Test empty token value contract."""
        empty_token_payload = {
            'token': ''
        }
        
        response = self.client.post(
            self.email_confirm_url,
            data=json.dumps(empty_token_payload),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Contract: Empty token error
        data = response.json()
        self.assertIn('errors', data)
        self.assertIn('token', data['errors'])
    
    def test_email_confirm_get_method_not_allowed_contract(self):
        """Test that GET method is not allowed for email confirmation."""
        response = self.client.get(
            f"{self.email_confirm_url}?token=some-token"
        )
        
        # Contract: Only POST method allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)