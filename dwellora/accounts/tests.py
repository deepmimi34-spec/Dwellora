import json

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .models import Profile
from .serializers import ProfileSerializer
from .views import ProfileDelete, ProfileList, ProfileUpdate


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
        self.assertNotIn('password', serializer.data)

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


class ProfilePrivacyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = Profile.objects.create_user(
            username='profile_owner',
            password='A-strong-password-948!',
            bio='Owner',
        )
        self.other = Profile.objects.create_user(
            username='other_member',
            password='A-strong-password-948!',
            bio='Other',
        )

    def test_profile_list_returns_only_authenticated_profile(self):
        request = self.factory.get('/profile/view_details/')
        force_authenticate(request, user=self.owner)

        response = ProfileList.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [self.owner.id])

    def test_profile_update_changes_only_authenticated_profile(self):
        request = self.factory.patch(
            '/profile/update/',
            {'bio': 'Updated by owner'},
            format='json',
        )
        force_authenticate(request, user=self.owner)

        response = ProfileUpdate.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.owner.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.owner.bio, 'Updated by owner')
        self.assertEqual(self.other.bio, 'Other')

    def test_profile_delete_deletes_only_authenticated_profile(self):
        request = self.factory.delete('/profile/delete/')
        force_authenticate(request, user=self.owner)

        response = ProfileDelete.as_view()(request)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Profile.objects.filter(pk=self.owner.pk).exists())
        self.assertTrue(Profile.objects.filter(pk=self.other.pk).exists())


class PublicApiIntegrationTests(TestCase):
    def test_property_and_service_discovery_routes_are_public(self):
        from property.models import Property

        Property.objects.create(
            title='Public apartment',
            property_type='Apartment',
            region='Ashanti',
        )

        property_response = self.client.get('/api/property/property/list/')
        service_response = self.client.get('/api/services/')

        self.assertEqual(property_response.status_code, 200)
        self.assertEqual(len(property_response.json()), 1)
        self.assertEqual(service_response.status_code, 200)

    def test_signup_then_jwt_login_and_profile_access(self):
        registration = self.client.post(
            '/api/accounts/profile/',
            data=json.dumps({
                'username': 'integration_user',
                'email': 'integration@example.com',
                'password': 'A-strong-password-948!',
                'bio': 'Integration account',
            }),
            content_type='application/json',
        )
        self.assertEqual(registration.status_code, 201)

        token_response = self.client.post(
            '/api/auth/token/',
            data=json.dumps({
                'username': 'integration_user',
                'password': 'A-strong-password-948!',
            }),
            content_type='application/json',
        )
        self.assertEqual(token_response.status_code, 200)
        access_token = token_response.json()['access']

        profile_response = self.client.get(
            '/api/accounts/profile/view_details/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
        )
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(len(profile_response.json()), 1)
        self.assertEqual(profile_response.json()[0]['username'], 'integration_user')
        self.assertFalse(profile_response.json()[0]['is_staff'])
