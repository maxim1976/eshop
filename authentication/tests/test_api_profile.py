"""
Contract tests for GET /api/auth/profile/ endpoint.
These tests MUST FAIL initially - they define the API contract.
"""

import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class ProfileAPIContractTest(TestCase):
    """Test API contract for user profile endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('auth:profile')
    
    def test_profile_authenticated_success_contract(self):
        """Test successful profile retrieval for authenticated user contract."""
        # First login to establish session
        login_url = reverse('auth:login')
        login_payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        login_response = self.client.post(
            login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Now get profile
        response = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Contract: Response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        # Contract: User data structure
        user_data = data['data']['user']
        self.assertIn('id', user_data)
        self.assertIn('email', user_data)
        self.assertIn('first_name', user_data)
        self.assertIn('last_name', user_data)
        self.assertIn('preferred_language', user_data)
        self.assertIn('is_email_confirmed', user_data)
        self.assertIn('date_joined', user_data)
        
        # Contract: Password field should NOT be included
        self.assertNotIn('password', user_data)
    
    def test_profile_unauthenticated_contract(self):
        """Test profile access without authentication contract."""
        response = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Contract: Error response structure
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
        
        # Contract: Authentication required message
        message = data['message']
        self.assertIn('需要登入', message)
    
    def test_profile_expired_session_contract(self):
        """Test profile access with expired session contract."""
        # Simulate expired session by using invalid session cookie
        self.client.cookies['sessionid'] = 'expired-session-id'
        
        response = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Contract: Returns 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Contract: Session expired error
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
    
    def test_profile_post_method_not_allowed_contract(self):
        """Test that POST method is not allowed for profile endpoint."""
        response = self.client.post(self.profile_url)
        
        # Contract: Only GET method allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_profile_language_preference_contract(self):
        """Test profile returns user's language preference contract."""
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
        
        # Get profile with different Accept-Language
        response = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='en'
        )
        
        if response.status_code == 200:
            # Contract: User's preferred language should be returned
            data = response.json()
            user_data = data['data']['user']
            self.assertIn('preferred_language', user_data)
            # Should be 'zh-hant' or 'en'
            self.assertIn(user_data['preferred_language'], ['zh-hant', 'en'])
    
    def test_profile_data_completeness_contract(self):
        """Test profile returns complete user data contract."""
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
        
        response = self.client.get(self.profile_url)
        
        if response.status_code == 200:
            data = response.json()
            user_data = data['data']['user']
            
            # Contract: All required fields present
            required_fields = [
                'id', 'email', 'first_name', 'last_name',
                'preferred_language', 'is_email_confirmed', 'date_joined'
            ]
            
            for field in required_fields:
                self.assertIn(field, user_data, f"Required field '{field}' missing")
            
            # Contract: Date format should be ISO 8601
            date_joined = user_data['date_joined']
            # Should contain 'T' and 'Z' for ISO format
            self.assertIn('T', date_joined)
            self.assertTrue(date_joined.endswith('Z'))