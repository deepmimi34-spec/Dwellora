from rest_framework.test import APIRequestFactory, force_authenticate
from django.test import TestCase

from accounts.models import Profile
from .models import Service
from .views import (
    ServiceCreate,
    ServiceDelete,
    ServiceDetail,
    ServiceList,
    ServiceUpdate,
)


class ServiceOwnershipTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.provider = Profile.objects.create_user(
            username='service_provider',
            password='A-strong-password-948!',
            bio='Provider',
        )
        self.other_user = Profile.objects.create_user(
            username='other_provider',
            password='A-strong-password-948!',
            bio='Other',
        )
        self.service = Service.objects.create(
            profile=self.provider,
            service_type='Real-estate agent',
            description='Residential property services in Kumasi.',
        )

    def test_service_directory_is_public(self):
        request = self.factory.get('/services/')
        response = ServiceList.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_service_detail_is_public(self):
        request = self.factory.get(f'/services/{self.service.pk}/')
        response = ServiceDetail.as_view()(request, pk=self.service.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.service.pk)

    def test_service_creation_assigns_authenticated_profile(self):
        request = self.factory.post('/services/create_service/', {
            'service_type': 'Architect',
            'description': 'Residential design and planning.',
        }, format='json')
        force_authenticate(request, user=self.other_user)

        response = ServiceCreate.as_view()(request)

        self.assertEqual(response.status_code, 201)
        created = Service.objects.get(pk=response.data['id'])
        self.assertEqual(created.profile_id, self.other_user.pk)

    def test_provider_cannot_create_a_second_service_profile(self):
        request = self.factory.post('/services/create_service/', {
            'service_type': 'Architect',
            'description': 'A second provider profile.',
        }, format='json')
        force_authenticate(request, user=self.provider)

        response = ServiceCreate.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Service.objects.filter(profile=self.provider).count(), 1)

    def test_provider_cannot_update_another_users_service(self):
        request = self.factory.patch(
            f'/services/update_service/{self.service.pk}/',
            {'description': 'Changed by another user.'},
            format='json',
        )
        force_authenticate(request, user=self.other_user)

        response = ServiceUpdate.as_view()(request, pk=self.service.pk)

        self.assertEqual(response.status_code, 404)
        self.service.refresh_from_db()
        self.assertEqual(
            self.service.description,
            'Residential property services in Kumasi.',
        )

    def test_provider_cannot_delete_another_users_service(self):
        request = self.factory.delete(
            f'/services/delete_service/{self.service.pk}/'
        )
        force_authenticate(request, user=self.other_user)

        response = ServiceDelete.as_view()(request, pk=self.service.pk)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Service.objects.filter(pk=self.service.pk).exists())

    def test_provider_can_update_own_service(self):
        request = self.factory.patch(
            f'/services/update_service/{self.service.pk}/',
            {'description': 'Updated service information.'},
            format='json',
        )
        force_authenticate(request, user=self.provider)

        response = ServiceUpdate.as_view()(request, pk=self.service.pk)

        self.assertEqual(response.status_code, 200)
        self.service.refresh_from_db()
        self.assertEqual(self.service.description, 'Updated service information.')

    def test_provider_can_delete_own_service(self):
        service_id = self.service.pk
        request = self.factory.delete(f'/services/delete_service/{service_id}/')
        force_authenticate(request, user=self.provider)

        response = ServiceDelete.as_view()(request, pk=service_id)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Service.objects.filter(pk=service_id).exists())
