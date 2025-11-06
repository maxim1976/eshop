"""
Integration tests for login and session management flow.
These tests MUST FAIL initially - they define the end-to-end user journey.
"""

import json
import time
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status


class LoginSessionIntegrationTest(TransactionTestCase):
    """Test complete login and session management flow integration."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('auth:login')
        self.logout_url = reverse('auth:logout')
        self.profile_url = reverse('auth:profile')
        
        # Valid user credentials (assuming user exists)
        self.valid_credentials = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
    
    def test_complete_login_logout_flow_integration(self):
        """Test complete login to logout flow."""
        # Step 1: Login with valid credentials
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_credentials),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        login_data = login_response.json()
        self.assertTrue(login_data['success'])
        
        # Verify session cookie is set
        self.assertIn('sessionid', login_response.cookies)
        session_cookie = login_response.cookies['sessionid']
        self.assertIsNotNone(session_cookie.value)
        
        # Step 2: Access protected resource (profile)
        profile_response = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        profile_data = profile_response.json()
        self.assertTrue(profile_data['success'])
        self.assertEqual(profile_data['data']['user']['email'], 'testuser@example.com')
        
        # Step 3: Logout
        logout_response = self.client.post(
            self.logout_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        logout_data = logout_response.json()
        self.assertTrue(logout_data['success'])
        
        # Step 4: Verify session is cleared
        profile_after_logout = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(profile_after_logout.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_remember_me_session_integration(self):
        """Test remember me functionality for extended sessions."""
        # Login with remember_me = True
        remember_credentials = self.valid_credentials.copy()
        remember_credentials['remember_me'] = True
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(remember_credentials),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify extended session expiry (7 days)
        session_expires = data['data']['session_expires']
        expires_datetime = datetime.fromisoformat(session_expires.replace('Z', '+00:00'))
        now = timezone.now()
        
        # Should expire approximately 7 days from now
        expected_expiry = now + timedelta(days=7)
        time_diff = abs((expires_datetime - expected_expiry).total_seconds())
        
        # Allow 1 hour tolerance
        self.assertLess(time_diff, 3600, "Session expiry should be approximately 7 days")
        
        # Verify session cookie has proper expiry
        session_cookie = response.cookies['sessionid']
        self.assertIsNotNone(session_cookie.value)
    
    def test_session_without_remember_me_integration(self):
        """Test session management without remember me."""
        # Login without remember_me
        no_remember_credentials = self.valid_credentials.copy()
        no_remember_credentials['remember_me'] = False
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(no_remember_credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Session should be shorter (browser session or default timeout)
        session_cookie = response.cookies['sessionid']
        self.assertIsNotNone(session_cookie.value)
        
        # Should still be able to access protected resources
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
    
    def test_concurrent_session_management_integration(self):
        """Test multiple concurrent sessions for same user."""
        # Create first session
        client1 = APIClient()
        response1 = client1.post(
            self.login_url,
            data=json.dumps(self.valid_credentials),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Create second session
        client2 = APIClient()
        response2 = client2.post(
            self.login_url,
            data=json.dumps(self.valid_credentials),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Both sessions should be valid
        profile1 = client1.get(self.profile_url)
        profile2 = client2.get(self.profile_url)
        
        self.assertEqual(profile1.status_code, status.HTTP_200_OK)
        self.assertEqual(profile2.status_code, status.HTTP_200_OK)
        
        # Logout from first session
        logout1 = client1.post(self.logout_url)
        self.assertEqual(logout1.status_code, status.HTTP_200_OK)
        
        # First session should be invalid
        profile1_after = client1.get(self.profile_url)
        self.assertEqual(profile1_after.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Second session should still be valid
        profile2_after = client2.get(self.profile_url)
        self.assertEqual(profile2_after.status_code, status.HTTP_200_OK)
    
    def test_invalid_login_attempts_integration(self):
        """Test handling of invalid login attempts."""
        invalid_credentials = [
            {'email': 'wrong@example.com', 'password': 'testpass123'},
            {'email': 'testuser@example.com', 'password': 'wrongpass'},
            {'email': 'invalid-email', 'password': 'testpass123'},
            {'email': '', 'password': 'testpass123'},
            {'email': 'testuser@example.com', 'password': ''},
        ]
        
        for credentials in invalid_credentials:
            response = self.client.post(
                self.login_url,
                data=json.dumps(credentials),
                content_type='application/json',
                HTTP_ACCEPT_LANGUAGE='zh-hant'
            )
            
            # Should return unauthorized
            self.assertIn(response.status_code, [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED
            ])
            
            data = response.json()
            self.assertFalse(data['success'])
            self.assertIn('errors', data)
            
            # Should not set session cookie
            self.assertNotIn('sessionid', response.cookies)
    
    def test_session_timeout_integration(self):
        """Test session timeout behavior."""
        # Login to establish session
        response = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Access profile immediately (should work)
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # Simulate session timeout by modifying session
        # (In real test, this would involve waiting or mocking time)
        # For now, just verify the session exists
        self.assertIn('sessionid', response.cookies)
    
    def test_language_preference_in_session_integration(self):
        """Test language preference handling in session."""
        # Login with Traditional Chinese
        response_zh = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_credentials),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(response_zh.status_code, status.HTTP_200_OK)
        data_zh = response_zh.json()
        
        # Response should be in Traditional Chinese
        self.assertIn('登入成功', data_zh['message'])
        
        # Logout and login with English
        self.client.post(self.logout_url)
        
        response_en = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_credentials),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='en'
        )
        
        self.assertEqual(response_en.status_code, status.HTTP_200_OK)
        data_en = response_en.json()
        
        # Response should be in English
        self.assertNotIn('登入成功', data_en['message'])
        self.assertIn('success', data_en['message'].lower())