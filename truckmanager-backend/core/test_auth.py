"""
Test script to verify authentication endpoints work correctly.
This can be run with: python manage.py test core.test_auth
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class AuthenticationEndpointTests(TestCase):
    """Test authentication endpoints to ensure they return proper error formats."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_with_wrong_password_returns_proper_error_format(self):
        """Test that login with wrong password returns non_field_errors."""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the error is in non_field_errors format (DRF standard)
        self.assertIn('non_field_errors', response.data)
        self.assertIsInstance(response.data['non_field_errors'], list)
        self.assertTrue(len(response.data['non_field_errors']) > 0)

    def test_login_with_email_credentials(self):
        """Test that login accepts email as identifier alongside username."""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test@example.com',
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_with_correct_credentials(self):
        """Test that login with correct credentials succeeds."""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_register_with_existing_username_returns_field_error(self):
        """Test that registration with existing username returns field error."""
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'testuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Field-specific errors should be keyed by field name
        self.assertIn('username', response.data)
    
    def test_register_with_mismatched_passwords_returns_field_error(self):
        """Test that registration with mismatched passwords returns field error."""
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)
    
    def test_register_with_valid_data(self):
        """Test that registration with valid data succeeds."""
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)