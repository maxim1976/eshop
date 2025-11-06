"""
Integration tests for complete user registration flow.
These tests MUST FAIL initially - they define the end-to-end user journey.
"""

import json
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status


class UserRegistrationIntegrationTest(TransactionTestCase):
    """Test complete user registration flow integration."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth:register')
        self.login_url = reverse('auth:login')
        self.confirm_email_url = reverse('auth:confirm-email')
        
        self.user_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': '李',
            'last_name': '小華',
            'preferred_language': 'zh-hant',
            'pdpa_consent': True
        }
    
    def test_complete_registration_flow_integration(self):
        """Test complete registration flow from signup to login."""
        # Step 1: Register new user
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('user_id', data['data'])
        user_id = data['data']['user_id']
        
        # Step 2: Verify confirmation email sent
        self.assertEqual(len(mail.outbox), 1)
        confirmation_email = mail.outbox[0]
        self.assertEqual(confirmation_email.to, ['newuser@example.com'])
        self.assertIn('確認', confirmation_email.subject)  # Traditional Chinese
        
        # Step 3: Extract confirmation token from email
        email_body = confirmation_email.body
        # Token should be in email body (implementation will define exact format)
        self.assertIn('token', email_body.lower())
        
        # Step 4: Attempt login before email confirmation (should fail)
        login_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        login_data_response = login_response.json()
        self.assertIn('email_confirmation', login_data_response['errors'])
        
        # Step 5: Confirm email with token
        confirmation_token = 'extracted-token-from-email'  # Mock token extraction
        confirm_response = self.client.post(
            self.confirm_email_url,
            data=json.dumps({'token': confirmation_token}),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        # Should succeed (though will fail until implemented)
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        
        # Step 6: Login after email confirmation (should succeed)
        login_response_after = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(login_response_after.status_code, status.HTTP_200_OK)
        login_data_after = login_response_after.json()
        self.assertTrue(login_data_after['success'])
        
        # Step 7: Verify user profile accessible
        profile_url = reverse('auth:profile')
        profile_response = self.client.get(
            profile_url,
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        profile_data = profile_response.json()
        user_profile = profile_data['data']['user']
        
        self.assertEqual(user_profile['email'], 'newuser@example.com')
        self.assertEqual(user_profile['first_name'], '李')
        self.assertEqual(user_profile['last_name'], '小華')
        self.assertEqual(user_profile['preferred_language'], 'zh-hant')
        self.assertTrue(user_profile['is_email_confirmed'])
    
    def test_duplicate_email_registration_integration(self):
        """Test duplicate email registration prevention."""
        # First registration
        response1 = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second registration with same email
        response2 = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        data = response2.json()
        self.assertFalse(data['success'])
        self.assertIn('email', data['errors'])
    
    def test_pdpa_consent_requirement_integration(self):
        """Test PDPA consent requirement in registration flow."""
        # Registration without PDPA consent
        invalid_data = self.user_data.copy()
        invalid_data['pdpa_consent'] = False
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='zh-hant'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('pdpa_consent', data['errors'])
        
        # Verify no user created and no email sent
        self.assertEqual(len(mail.outbox), 0)
    
    def test_language_preference_integration(self):
        """Test language preference setting and usage in registration."""
        # Register with English preference
        english_data = self.user_data.copy()
        english_data['email'] = 'english@example.com'
        english_data['preferred_language'] = 'en'
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(english_data),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='en'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify confirmation email sent in English
        self.assertEqual(len(mail.outbox), 1)
        confirmation_email = mail.outbox[0]
        # Email should be in English, not Traditional Chinese
        self.assertNotIn('確認', confirmation_email.subject)
        # Should contain English terms
        email_content = confirmation_email.body.lower()
        self.assertIn('confirm', email_content)
    
    def test_password_validation_integration(self):
        """Test password validation in registration flow."""
        # Test various invalid passwords
        invalid_passwords = [
            ('123', 'Too short'),
            ('abcdefgh', 'No numbers'),
            ('12345678', 'No letters'),
            ('', 'Empty password')
        ]
        
        for invalid_password, description in invalid_passwords:
            invalid_data = self.user_data.copy()
            invalid_data['email'] = f'test{invalid_password}@example.com'
            invalid_data['password'] = invalid_password
            invalid_data['password_confirm'] = invalid_password
            
            response = self.client.post(
                self.register_url,
                data=json.dumps(invalid_data),
                content_type='application/json',
                HTTP_ACCEPT_LANGUAGE='zh-hant'
            )
            
            self.assertEqual(
                response.status_code, 
                status.HTTP_400_BAD_REQUEST,
                f"Password validation failed for: {description}"
            )
            
            data = response.json()
            self.assertIn('password', data['errors'], f"Missing password error for: {description}")