"""
System integration tests for the complete authentication system.
Tests the full user journey from registration to login.
"""

import json
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser, EmailConfirmationToken


class SystemIntegrationTest(TransactionTestCase):
    """Test complete authentication system integration."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth:register')
        self.login_url = reverse('auth:login')
        self.logout_url = reverse('auth:logout')
        self.confirm_email_url = reverse('auth:confirm-email')
        self.profile_url = reverse('auth:profile')
        
        self.user_data = {
            'email': 'integration@test.com',
            'password': 'integrationtest123',
            'password_confirm': 'integrationtest123',
            'first_name': '整合',
            'last_name': '測試',
            'preferred_language': 'zh-hant',
            'pdpa_consent': True
        }
    
    def test_complete_user_journey_integration(self):
        """Test the complete user journey from registration to authenticated access."""
        
        # Step 1: Register new user
        print("Step 1: Testing user registration...")
        register_response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        register_data = register_response.json()
        self.assertTrue(register_data['success'])
        self.assertIn('註冊成功', register_data['message'])
        
        # Verify user was created but is inactive
        user = CustomUser.objects.get(email='integration@test.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_email_confirmed)
        self.assertEqual(user.preferred_language, 'zh-hant')
        self.assertTrue(user.pdpa_consent)
        
        # Step 2: Verify email confirmation token was created
        print("Step 2: Testing email confirmation token creation...")
        confirmation_token = EmailConfirmationToken.objects.get(user=user)
        self.assertIsNotNone(confirmation_token.token)
        self.assertEqual(confirmation_token.email, user.email)
        self.assertFalse(confirmation_token.is_used)
        
        # Step 3: Verify confirmation email was sent
        print("Step 3: Testing email sending...")
        self.assertEqual(len(mail.outbox), 1)
        confirmation_email = mail.outbox[0]
        self.assertEqual(confirmation_email.to, ['integration@test.com'])
        self.assertIn('確認', confirmation_email.subject)  # Traditional Chinese
        
        # Step 4: Attempt login before email confirmation (should fail)
        print("Step 4: Testing login before email confirmation...")
        login_data = {
            'email': 'integration@test.com',
            'password': 'integrationtest123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        login_response_data = login_response.json()
        self.assertIn('email_confirmation', login_response_data['errors'])
        
        # Step 5: Confirm email
        print("Step 5: Testing email confirmation...")
        confirm_response = self.client.post(
            self.confirm_email_url,
            data=json.dumps({'token': str(confirmation_token.token)}),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        confirm_data = confirm_response.json()
        self.assertTrue(confirm_data['success'])
        self.assertIn('確認成功', confirm_data['message'])
        
        # Verify user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_email_confirmed)
        
        # Step 6: Login after email confirmation (should succeed)
        print("Step 6: Testing login after email confirmation...")
        login_response_after = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(login_response_after.status_code, status.HTTP_200_OK)
        login_data_after = login_response_after.json()
        self.assertTrue(login_data_after['success'])
        self.assertIn('登入成功', login_data_after['message'])
        
        # Step 7: Access protected profile endpoint
        print("Step 7: Testing authenticated profile access...")
        profile_response = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        profile_data = profile_response.json()
        self.assertTrue(profile_data['success'])
        
        user_profile = profile_data['data']['user']
        self.assertEqual(user_profile['email'], 'integration@test.com')
        self.assertEqual(user_profile['first_name'], '整合')
        self.assertEqual(user_profile['last_name'], '測試')
        self.assertEqual(user_profile['preferred_language'], 'zh-hant')
        self.assertTrue(user_profile['is_email_confirmed'])
        
        # Step 8: Logout
        print("Step 8: Testing logout...")
        logout_response = self.client.post(
            self.logout_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        logout_data = logout_response.json()
        self.assertTrue(logout_data['success'])
        self.assertIn('登出', logout_data['message'])
        
        # Step 9: Verify access is blocked after logout
        print("Step 9: Testing access after logout...")
        profile_after_logout = self.client.get(
            self.profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(profile_after_logout.status_code, status.HTTP_401_UNAUTHORIZED)
        
        print("✅ Complete user journey integration test passed!")
    
    def test_api_error_localization(self):
        """Test that API errors are returned in the correct language."""
        
        # Test Traditional Chinese error messages
        invalid_data = {
            'email': 'invalid-email',
            'password': 'short',
            'password_confirm': 'different',
            'pdpa_consent': False
        }
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('註冊失敗', data['message'])
        
        # Should have errors in Traditional Chinese
        self.assertIn('errors', data)
        
        print("✅ API error localization test passed!")
    
    def test_system_health_and_availability(self):
        """Test system health and basic availability."""
        
        # Test health endpoint
        health_response = self.client.get('/health/')
        self.assertEqual(health_response.status_code, status.HTTP_200_OK)
        
        health_data = health_response.json()
        self.assertEqual(health_data['status'], 'healthy')
        self.assertEqual(health_data['service'], 'eshop')
        
        # Test all authentication endpoints are reachable (even if they return errors)
        endpoints_to_test = [
            ('/api/auth/register/', 'POST'),
            ('/api/auth/login/', 'POST'),
            ('/api/auth/logout/', 'POST'),
            ('/api/auth/password-reset/', 'POST'),
            ('/api/auth/password-reset-confirm/', 'POST'),
            ('/api/auth/confirm-email/', 'POST'),
            ('/api/auth/profile/', 'GET'),
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == 'GET':
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint, data='{}', content_type='application/json')
            
            # Should not return 404 (endpoint exists) or 500 (server error)
            self.assertNotEqual(response.status_code, 404, f"Endpoint {endpoint} not found")
            self.assertNotEqual(response.status_code, 500, f"Server error at {endpoint}")
        
        print("✅ System health and availability test passed!")