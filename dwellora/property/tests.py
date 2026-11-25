from django.test import TestCase

from .models import Property


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
