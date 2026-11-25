from datetime import date

from django.test import TestCase

from hostels.models import HostelBuilding, HostelType, HostelUnit
from property.models import Property
from .models import HostelBooking


class HostelBookingStringTests(TestCase):
    def test_booking_string_uses_existing_unit_and_date_fields(self):
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
        unit = HostelUnit.objects.create(
            hostel_type=room_type,
            unit_name='Room 12',
            status='available',
        )
        booking = HostelBooking.objects.create(
            hostel=unit,
            start_date=date(2027, 1, 5),
            end_date=date(2027, 6, 30),
        )

        self.assertEqual(
            str(booking),
            'Room 12 - 2027-01-05 to 2027-06-30',
        )
