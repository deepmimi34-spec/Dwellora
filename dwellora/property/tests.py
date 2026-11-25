from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from .models import Property
from .views import PropertyDeleteView, PropertyDetailView, PropertyUpdate


class PropertyCompletenessTests(TestCase):
    def test_property_with_title_and_region_is_complete(self):
        property_record = Property(
            title='Two-bedroom apartment',
            property_type='Apartment',
            region='Ashanti',
        )

        self.assertTrue(property_record.is_property_complete())

    def test_city_is_optional_for_completeness(self):
        property_record = Property(
            title='Single room',
            property_type='Hostel',
            region='Greater Accra',
            city='',
        )

        self.assertTrue(property_record.is_property_complete())

    def test_missing_title_is_incomplete(self):
        property_record = Property(
            title='',
            property_type='Apartment',
            region='Ashanti',
        )

        self.assertFalse(property_record.is_property_complete())

    def test_missing_region_is_incomplete(self):
        property_record = Property(
            title='Two-bedroom apartment',
            property_type='Apartment',
            region='',
        )

        self.assertFalse(property_record.is_property_complete())


class PropertyEndpointAccessTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.member = Profile.objects.create_user(
            username='property_member',
            password='A-strong-password-948!',
            bio='Member',
        )
        self.staff = Profile.objects.create_user(
            username='property_staff',
            password='A-strong-password-948!',
            bio='Staff',
            is_staff=True,
        )
        self.property_record = Property.objects.create(
            title='Two-bedroom apartment',
            property_type='Apartment',
            region='Ashanti',
            city='Kumasi',
        )

    def test_detail_endpoint_returns_one_property(self):
        request = self.factory.get('/property/1/detail/')

        response = PropertyDetailView.as_view()(
            request,
            pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.property_record.pk)
        self.assertEqual(response.data['title'], 'Two-bedroom apartment')

    def test_non_staff_cannot_update_property(self):
        request = self.factory.patch(
            f'/property/{self.property_record.pk}/update/',
            {'title': 'Changed by member'},
            format='json',
        )
        force_authenticate(request, user=self.member)

        response = PropertyUpdate.as_view()(
            request,
            pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 403)
        self.property_record.refresh_from_db()
        self.assertEqual(self.property_record.title, 'Two-bedroom apartment')

    def test_staff_can_update_property(self):
        request = self.factory.patch(
            f'/property/{self.property_record.pk}/update/',
            {'title': 'Updated by staff'},
            format='json',
        )
        force_authenticate(request, user=self.staff)

        response = PropertyUpdate.as_view()(
            request,
            pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 200)
        self.property_record.refresh_from_db()
        self.assertEqual(self.property_record.title, 'Updated by staff')

    def test_non_staff_cannot_delete_property(self):
        property_id = self.property_record.pk
        request = self.factory.delete(f'/property/{property_id}/delete/')
        force_authenticate(request, user=self.member)

        response = PropertyDeleteView.as_view()(
            request,
            pk=property_id,
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Property.objects.filter(pk=property_id).exists())

    def test_staff_can_delete_property(self):
        property_id = self.property_record.pk
        request = self.factory.delete(f'/property/{property_id}/delete/')
        force_authenticate(request, user=self.staff)

        response = PropertyDeleteView.as_view()(
            request,
            pk=property_id,
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Property.objects.filter(pk=property_id).exists())
