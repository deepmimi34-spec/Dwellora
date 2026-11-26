from django.test import SimpleTestCase, TestCase
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.urls import reverse, resolve
from rest_framework.test import APIRequestFactory

from accounts.models import Profile
from property.models import Property
from property.listing_models import Listing, PropertyOwnership, PractitionerLicense, ListingAuthorization
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


    def test_review_notes_are_visible_only_to_staff(self):
        agent = Profile.objects.create_user(
            username="privacy_agent", password="Strong-password-1!"
        )
        staff = Profile.objects.create_user(
            username="privacy_staff", password="Strong-password-1!", is_staff=True
        )
        ownership = PropertyOwnership.objects.create(
            property=self.property,
            claimant=self.owner,
            review_note="Internal ownership verification details",
        )
        license_record = PractitionerLicense.objects.create(
            profile=agent,
            license_number="REAC-PRIVACY-001",
            license_type=PractitionerLicense.LicenseType.AGENT,
            review_note="Internal licence verification details",
        )
        authorization = ListingAuthorization.objects.create(
            property=self.property,
            ownership=ownership,
            lister=agent,
            authority_type=ListingAuthorization.AuthorityType.AGENT,
            review_note="Internal authorization review details",
        )

        records = (
            (PropertyOwnershipSerializer, ownership, self.owner, "Internal ownership verification details"),
            (PractitionerLicenseSerializer, license_record, agent, "Internal licence verification details"),
            (ListingAuthorizationSerializer, authorization, agent, "Internal authorization review details"),
        )
        for serializer_class, instance, subject, expected_note in records:
            with self.subTest(serializer=serializer_class.__name__):
                subject_request = self.factory.get("/")
                subject_request.user = subject
                subject_data = serializer_class(
                    instance, context={"request": subject_request}
                ).data
                self.assertIsNone(subject_data["review_note"])

                staff_request = self.factory.get("/")
                staff_request.user = staff
                staff_data = serializer_class(
                    instance, context={"request": staff_request}
                ).data
                self.assertEqual(staff_data["review_note"], expected_note)



class ListingCreationAuthorityTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = Profile.objects.create_user(
            username="listing_owner", password="Strong-password-1!"
        )
        self.other_user = Profile.objects.create_user(
            username="unverified_lister", password="Strong-password-1!"
        )
        self.staff = Profile.objects.create_user(
            username="listing_staff", password="Strong-password-1!", is_staff=True
        )
        self.property = Property.objects.create(
            title="Verified Listing Property",
            property_type="Apartment",
            region="Ashanti",
            city="Kumasi",
        )

    def _request(self, user):
        request = self.factory.post("/api/property/listings/create/")
        request.user = user
        return request

    def _payload(self):
        return {
            "property": self.property.pk,
            "offer_type": Listing.OfferType.RENT,
            "headline": "Apartment for rent",
            "price": "2500.00",
            "currency": "GHS",
            "billing_period": "month",
        }

    def test_unverified_user_cannot_create_listing_for_property(self):
        serializer = ListingSerializer(
            data=self._payload(), context={"request": self._request(self.other_user)}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("property", serializer.errors)

    def test_verified_owner_can_create_listing(self):
        PropertyOwnership.objects.create(
            property=self.property,
            claimant=self.owner,
            status=PropertyOwnership.Status.VERIFIED,
            reviewed_by=self.staff,
            reviewed_at=timezone.now(),
        )
        serializer = ListingSerializer(
            data=self._payload(), context={"request": self._request(self.owner)}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        listing = serializer.save()
        self.assertEqual(listing.lister_id, self.owner.pk)
        self.assertEqual(listing.property_id, self.property.pk)

    def test_client_cannot_assign_another_lister(self):
        PropertyOwnership.objects.create(
            property=self.property,
            claimant=self.owner,
            status=PropertyOwnership.Status.VERIFIED,
            reviewed_by=self.staff,
            reviewed_at=timezone.now(),
        )
        payload = self._payload()
        payload["lister"] = self.other_user.pk
        serializer = ListingSerializer(
            data=payload, context={"request": self._request(self.owner)}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        listing = serializer.save()
        self.assertEqual(listing.lister_id, self.owner.pk)
