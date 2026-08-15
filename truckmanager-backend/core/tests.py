from django.contrib.auth.models import User
from django.test import TestCase

from core.models import UserProfile, get_user_role


class UserRoleTests(TestCase):
    def test_user_profile_role_is_created_for_owner_registration(self):
        user = User.objects.create_user(
            username='owner1',
            email='owner1@test.com',
            password='pass1234',
            first_name='Pro',
            last_name='Prietaire',
        )

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = 'OWNER'
        profile.save()

        self.assertEqual(profile.role, 'OWNER')
        self.assertTrue(UserProfile.objects.filter(user=user, role='OWNER').exists())

    def test_user_profile_role_is_created_for_admin_registration(self):
        user = User.objects.create_user(
            username='admin1',
            email='admin1@test.com',
            password='pass1234',
            first_name='Admin',
            last_name='User',
        )

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = 'ADMIN'
        profile.save()

        self.assertEqual(profile.role, 'ADMIN')
        self.assertTrue(UserProfile.objects.filter(user=user, role='ADMIN').exists())

    def test_get_user_role_returns_profile_role_for_authenticated_user(self):
        user = User.objects.create_user(
            username='owner_role_check',
            email='owner_role_check@test.com',
            password='pass1234',
        )

        profile = user.profile
        profile.role = 'ADMIN'
        profile.save()

        self.assertEqual(get_user_role(user), 'ADMIN')
        self.assertEqual(get_user_role(User()), 'OWNER')
