from django.test import SimpleTestCase, TestCase
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse, resolve
from rest_framework.test import APIRequestFactory

from accounts.models import Profile
from property.models import Property
from property.listing_models import Listing
from property.listing_serializers import (
    PractitionerLicenseSerializer,
    PropertyOwnershipSerializer,
    ListingAuthorizationSerializer,
    ListingSerializer,
)


class ListingAPIRouteTests(SimpleTestCase):
    def test_owner_and_listing_routes_are_registered(self):
        routes = {
            "ownership_claim_create": "/api/property/ownership/claims/",
            "ownership_claim_list": "/api/property/ownership/claims/mine/",
            "practitioner_license_list_create": "/api/property/licenses/",
            "listing_authorization_create": "/api/property/authorizations/",
            "listing_create": "/api/property/listings/create/",
            "my_listings": "/api/property/listings/my/",
            "public_listings": "/api/property/listings/public/",
            "listing_submit": "/api/property/listings/7/submit/",
            "listing_availability_confirm": "/api/property/listings/7/availability/",
            "listing_charge_list_create": "/api/property/listings/7/charges/",
        }
        for name, expected_path in routes.items():
            with self.subTest(route=name):
                self.assertEqual(reverse(name, kwargs={"pk": 7} if name in {
                    "listing_submit", "listing_availability_confirm"
                } else {"listing_pk": 7} if name == "listing_charge_list_create" else None), expected_path)
                resolve(expected_path)


class ListingAPISerializerPrivacyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = Profile.objects.create_user(
            username="privacy_owner", password="Strong-password-1!", bio="owner"
        )
        self.property = Property.objects.create(
            title="Privacy Test Property", property_type="Apartment",
            region="Ashanti", city="Kumasi",
        )

    def test_evidence_storage_references_are_write_only(self):
        for serializer_class in (
            PractitionerLicenseSerializer,
            PropertyOwnershipSerializer,
            ListingAuthorizationSerializer,
        ):
            with self.subTest(serializer=serializer_class.__name__):
                serializer = serializer_class()
                self.assertTrue(serializer.fields["evidence_reference"].write_only)

    def test_public_listing_serialization_hides_internal_moderation_note(self):
        listing = Listing.objects.create(
            property=self.property,
            lister=self.owner,
            offer_type=Listing.OfferType.RENT,
            headline="Private moderation note",
            price=100,
            moderation_note="Internal staff-only review context",
        )
        anonymous_request = self.factory.get("/api/property/listings/public/")
        anonymous_request.user = AnonymousUser()
        public_data = ListingSerializer(
            listing, context={"request": anonymous_request}
        ).data
        self.assertIsNone(public_data["moderation_note"])

        owner_request = self.factory.get("/api/property/listings/my/")
        owner_request.user = self.owner
        owner_data = ListingSerializer(
            listing, context={"request": owner_request}
        ).data
        self.assertEqual(
            owner_data["moderation_note"], "Internal staff-only review context"
        )
