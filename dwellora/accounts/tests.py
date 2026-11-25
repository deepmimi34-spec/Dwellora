from django.contrib.auth.hashers import check_password
from django.test import TestCase

from .models import Profile
from .serializers import ProfileSerializer


class ProfilePasswordTests(TestCase):
    def test_account_creation_hashes_password(self):
        raw_password = 'A-strong-password-948!'
        serializer = ProfileSerializer(data={
            'username': 'new_member',
            'email': 'member@example.com',
            'password': raw_password,
            'bio': 'Dwellora member',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()

        self.assertNotEqual(profile.password, raw_password)
        self.assertTrue(check_password(raw_password, profile.password))

    def test_account_creation_requires_password(self):
        serializer = ProfileSerializer(data={
            'username': 'missing_password',
            'email': 'missing@example.com',
            'bio': 'Dwellora member',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_profile_update_without_password_keeps_existing_password(self):
        profile = Profile.objects.create_user(
            username='existing_member',
            email='existing@example.com',
            password='A-strong-password-948!',
            bio='Original bio',
        )
        original_hash = profile.password

        serializer = ProfileSerializer(
            profile,
            data={'bio': 'Updated bio'},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_profile = serializer.save()

        self.assertEqual(updated_profile.password, original_hash)
        self.assertTrue(updated_profile.check_password('A-strong-password-948!'))

    def test_profile_update_hashes_new_password(self):
        profile = Profile.objects.create_user(
            username='password_change',
            password='A-strong-password-948!',
            bio='Dwellora member',
        )
        raw_new_password = 'Another-strong-password-638!'

        serializer = ProfileSerializer(
            profile,
            data={'password': raw_new_password},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_profile = serializer.save()

        self.assertTrue(updated_profile.check_password(raw_new_password))
