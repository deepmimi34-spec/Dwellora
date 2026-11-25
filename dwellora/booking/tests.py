from datetime import date

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from hostels.models import HostelBuilding, HostelType, HostelUnit
from property.models import Property
from .models import HostelBooking
from .serializers import HostelBookingSerializer
from .views import (
    HostelBookingCreateView,
    HostelBookingDestroyView,
    HostelBookingUpdateView,
    HostelBookingView,
)


class BookingFixtureMixin:
    def create_unit(self, status='available'):
        property_record = Property.objects.create(
            title='Student accommodation',
            property_type='Hostel',
            region='Ashanti',
            city='Kumasi',
        )
        building = HostelBuilding.objects.create(
            property=property_record,
            hostel_name='North Hall',
            town='Kumasi',
        )
        room_type = HostelType.objects.create(
            hostel_building=building,
            name='2 in a room',
            bathrooms=1,
            price='1500.00',
        )
        return HostelUnit.objects.create(
            hostel_type=room_type,
            unit_name='Room 12',
            status=status,
        )


class HostelBookingStringTests(BookingFixtureMixin, TestCase):
    def test_booking_string_uses_existing_unit_and_date_fields(self):
        unit = self.create_unit()
        booking = HostelBooking.objects.create(
            hostel=unit,
            start_date=date(2027, 1, 5),
            end_date=date(2027, 6, 30),
        )

        self.assertEqual(
            str(booking),
            'Room 12 - 2027-01-05 to 2027-06-30',
        )


class HostelBookingValidationTests(BookingFixtureMixin, TestCase):
    def test_end_date_must_be_after_start_date(self):
        unit = self.create_unit()
        serializer = HostelBookingSerializer(data={
            'hostel': unit.pk,
            'start_date': '2027-06-30',
            'end_date': '2027-06-30',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_unavailable_unit_cannot_be_booked(self):
        unit = self.create_unit(status='rented')
        serializer = HostelBookingSerializer(data={
            'hostel': unit.pk,
            'start_date': '2027-06-01',
            'end_date': '2027-06-30',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('hostel', serializer.errors)


class HostelBookingPermissionTests(BookingFixtureMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.member = Profile.objects.create_user(
            username='booking_member',
            password='A-strong-password-948!',
            bio='Member',
        )
        self.staff = Profile.objects.create_user(
            username='booking_staff',
            password='A-strong-password-948!',
            bio='Staff',
            is_staff=True,
        )
        unit = self.create_unit()
        self.booking = HostelBooking.objects.create(
            hostel=unit,
            start_date=date(2027, 1, 5),
            end_date=date(2027, 6, 30),
        )

    def test_non_staff_cannot_list_bookings(self):
        request = self.factory.get('/booking/hostel_view/')
        force_authenticate(request, user=self.member)

        response = HostelBookingView.as_view()(request)

        self.assertEqual(response.status_code, 403)

    def test_non_staff_cannot_create_bookings(self):
        request = self.factory.post('/booking/hostel_booking/', {
            'hostel': self.booking.hostel_id,
            'start_date': '2027-07-01',
            'end_date': '2027-12-31',
        }, format='json')
        force_authenticate(request, user=self.member)

        response = HostelBookingCreateView.as_view()(request)

        self.assertEqual(response.status_code, 403)

    def test_non_staff_cannot_update_bookings(self):
        request = self.factory.patch(
            f'/booking/hostel_update/{self.booking.pk}/',
            {'end_date': '2027-07-01'},
            format='json',
        )
        force_authenticate(request, user=self.member)

        response = HostelBookingUpdateView.as_view()(
            request,
            pk=self.booking.pk,
        )

        self.assertEqual(response.status_code, 403)

    def test_non_staff_cannot_delete_bookings(self):
        request = self.factory.delete(
            f'/booking/hostel_delete/{self.booking.pk}/'
        )
        force_authenticate(request, user=self.member)

        response = HostelBookingDestroyView.as_view()(
            request,
            pk=self.booking.pk,
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(HostelBooking.objects.filter(pk=self.booking.pk).exists())

    def test_staff_can_list_bookings(self):
        request = self.factory.get('/booking/hostel_view/')
        force_authenticate(request, user=self.staff)

        response = HostelBookingView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
