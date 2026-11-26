from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate
from unittest.mock import patch

from accounts.models import Profile
from property.models import Property
from property.listing_models import PractitionerLicense, PropertyOwnership, ListingAuthorization, Listing, ListingAvailabilityConfirmation, ListingCharge
from property.listing_serializers import PractitionerLicenseSerializer, ListingSerializer
from property.listing_views import (
    OwnershipClaimCreate, OwnershipClaimReview, PractitionerLicenseReview,
    ListingAuthorizationCreate, ListingAuthorizationReview,
    ListingCreate, ListingSubmit, ListingModeration, ListingAvailabilityConfirm, ListingChargeListCreate,
    PublicListingList, MyListingList, ListingUpdate, ListingDelete,
)


class ListingArchitectureTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = Profile.objects.create_user(username="owner_a", password="Strong-password-1!", bio="owner")
        self.agent = Profile.objects.create_user(username="agent_a", password="Strong-password-1!", bio="agent")
        self.member = Profile.objects.create_user(username="member_a", password="Strong-password-1!", bio="member")
        self.staff = Profile.objects.create_user(username="staff_a", password="Strong-password-1!", bio="staff", is_staff=True)
        self.property = Property.objects.create(title="Central Kumasi Apartment", property_type="Apartment", region="Ashanti", city="Kumasi")

    def claim(self, user=None):
        request = self.factory.post("/ownership/claims/", {
            "property": self.property.pk,
            "ownership_type": "individual",
            "evidence_type": "Ownership document",
            "evidence_reference": "private://test-evidence",
        }, format="json")
        force_authenticate(request, user=user or self.owner)
        response = OwnershipClaimCreate.as_view()(request)
        self.assertEqual(response.status_code, 201)
        return PropertyOwnership.objects.get(pk=response.data["id"])

    def verify_claim(self, claim):
        request = self.factory.post(f"/ownership/claims/{claim.pk}/review/", {
            "status": PropertyOwnership.Status.VERIFIED,
            "review_note": "Evidence checked in test.",
        }, format="json")
        force_authenticate(request, user=self.staff)
        response = OwnershipClaimReview.as_view()(request, pk=claim.pk)
        self.assertEqual(response.status_code, 200)
        claim.refresh_from_db()


    def verify_agent_license(self):
        license_record = PractitionerLicense.objects.create(
            profile=self.agent,
            license_number="REAC/2026/A/TEST-001",
            license_type=PractitionerLicense.LicenseType.AGENT,
            source_url="https://reac.gov.gh/public-registry-search/",
        )
        license_record.review(
            self.staff,
            PractitionerLicense.Status.VERIFIED,
            source_checked_at=timezone.now(),
            valid_until=timezone.localdate() + timedelta(days=365),
            note="Registry entry checked in test.",
        )
        return license_record

    def authorize_agent(self, claim):
        self.verify_agent_license()
        request = self.factory.post("/authorizations/", {
            "property": self.property.pk,
            "ownership": claim.pk,
            "authority_type": ListingAuthorization.AuthorityType.AGENT,
            "evidence_type": "Signed mandate",
            "evidence_reference": "private://mandate",
        }, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingAuthorizationCreate.as_view()(request)
        self.assertEqual(response.status_code, 201)
        auth = ListingAuthorization.objects.get(pk=response.data["id"])
        review_request = self.factory.post(f"/authorizations/{auth.pk}/review/", {
            "status": ListingAuthorization.Status.APPROVED,
            "review_note": "Mandate reviewed.",
        }, format="json")
        force_authenticate(review_request, user=self.staff)
        review_response = ListingAuthorizationReview.as_view()(review_request, pk=auth.pk)
        self.assertEqual(review_response.status_code, 200)
        auth.refresh_from_db()
        return auth

    def listing_payload(self, auth=None):
        return {
            "property": self.property.pk,
            "authorization": auth.pk if auth else None,
            "offer_type": Listing.OfferType.RENT,
            "headline": "Two-bedroom home for rent",
            "description": "Test listing.",
            "price": "1500.00",
            "currency": "GHS",
            "billing_period": "month",
            "advance_months": 12,
            "deposit_amount": "500.00",
            "agent_fee_amount": "1000.00",
            "viewing_fee_amount": "0.00",
            "service_charge_amount": "100.00",
            "other_fees_amount": "0.00",
            "costs_disclosed": True,
        }

    def test_claim_is_bound_to_authenticated_user(self):
        claim = self.claim()
        self.assertEqual(claim.claimant_id, self.owner.pk)
        self.assertEqual(claim.status, PropertyOwnership.Status.CLAIMED)

    def test_non_staff_cannot_verify_ownership(self):
        claim = self.claim()
        request = self.factory.post(f"/ownership/claims/{claim.pk}/review/", {"status": "verified"})
        force_authenticate(request, user=self.owner)
        response = OwnershipClaimReview.as_view()(request, pk=claim.pk)
        self.assertEqual(response.status_code, 403)
        claim.refresh_from_db()
        self.assertEqual(claim.status, PropertyOwnership.Status.CLAIMED)

    def test_ownership_revocation_rolls_back_if_listing_pause_fails(self):
        claim = self.claim()
        self.verify_claim(claim)
        Listing.objects.create(
            property=self.property,
            lister=self.owner,
            offer_type=Listing.OfferType.RENT,
            headline="Published test listing",
            price="1000.00",
            status=Listing.Status.PUBLISHED,
            moderated_by=self.staff,
            moderated_at=timezone.now(),
        )
        with patch.object(Listing, "moderate", side_effect=RuntimeError("simulated pause failure")):
            with self.assertRaises(RuntimeError):
                claim.review(self.staff, PropertyOwnership.Status.REVOKED, "Revocation test")
        claim.refresh_from_db()
        self.assertEqual(claim.status, PropertyOwnership.Status.VERIFIED)

    def test_authorization_revocation_rolls_back_if_listing_pause_fails(self):
        claim = self.claim()
        self.verify_claim(claim)
        authorization = self.authorize_agent(claim)
        listing = Listing.objects.create(
            property=self.property,
            lister=self.agent,
            authorization=authorization,
            offer_type=Listing.OfferType.RENT,
            headline="Published agent listing",
            price="1000.00",
            status=Listing.Status.PUBLISHED,
            moderated_by=self.staff,
            moderated_at=timezone.now(),
        )

        with patch.object(Listing, "moderate", side_effect=RuntimeError("simulated pause failure")):
            with self.assertRaises(RuntimeError):
                authorization.review(
                    self.staff,
                    ListingAuthorization.Status.REVOKED,
                    "Revocation rollback test",
                )

        authorization.refresh_from_db()
        listing.refresh_from_db()
        self.assertEqual(authorization.status, ListingAuthorization.Status.APPROVED)
        self.assertEqual(listing.status, Listing.Status.PUBLISHED)

    def test_license_suspension_rolls_back_if_listing_pause_fails(self):
        claim = self.claim()
        self.verify_claim(claim)
        license_record = self.verify_agent_license()
        authorization = self.authorize_agent(claim)
        listing = Listing.objects.create(
            property=self.property,
            lister=self.agent,
            authorization=authorization,
            offer_type=Listing.OfferType.RENT,
            headline="Published licensed-agent listing",
            price="1000.00",
            status=Listing.Status.PUBLISHED,
            moderated_by=self.staff,
            moderated_at=timezone.now(),
        )

        with patch.object(Listing, "moderate", side_effect=RuntimeError("simulated pause failure")):
            with self.assertRaises(RuntimeError):
                license_record.review(
                    self.staff,
                    PractitionerLicense.Status.SUSPENDED,
                    note="Suspension rollback test",
                )

        license_record.refresh_from_db()
        authorization.refresh_from_db()
        listing.refresh_from_db()
        self.assertEqual(license_record.status, PractitionerLicense.Status.VERIFIED)
        self.assertEqual(authorization.status, ListingAuthorization.Status.APPROVED)
        self.assertEqual(listing.status, Listing.Status.PUBLISHED)

    def test_owner_claim_can_be_verified_by_staff(self):
        claim = self.claim()
        self.verify_claim(claim)
        self.assertEqual(claim.status, PropertyOwnership.Status.VERIFIED)
        self.assertEqual(claim.reviewed_by_id, self.staff.pk)
        self.assertIsNotNone(claim.reviewed_at)

    def test_duplicate_ownership_claim_is_rejected(self):
        self.claim()
        request = self.factory.post("/ownership/claims/", {"property": self.property.pk}, format="json")
        force_authenticate(request, user=self.owner)
        response = OwnershipClaimCreate.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_agent_requires_verified_owner_claim(self):
        claim = self.claim()
        request = self.factory.post("/authorizations/", {
            "property": self.property.pk,
            "ownership": claim.pk,
            "authority_type": "agent",
        }, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingAuthorizationCreate.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_authorization_must_match_claimed_property(self):
        claim = self.claim()
        other = Property.objects.create(title="Other property", property_type="House", region="Greater Accra")
        claim.property = other
        claim.save()
        self.verify_claim(claim)
        request = self.factory.post("/authorizations/", {
            "property": self.property.pk,
            "ownership": claim.pk,
            "authority_type": "agent",
        }, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingAuthorizationCreate.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_owner_with_unverified_claim_cannot_create_listing_draft(self):
        self.claim()
        request = self.factory.post("/listings/create/", self.listing_payload(), format="json")
        force_authenticate(request, user=self.owner)
        response = ListingCreate.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Listing.objects.filter(property=self.property, lister=self.owner).exists())

    def test_verified_owner_can_submit_and_staff_publish(self):
        claim = self.claim()
        self.verify_claim(claim)
        request = self.factory.post("/listings/create/", self.listing_payload(), format="json")
        force_authenticate(request, user=self.owner)
        response = ListingCreate.as_view()(request)
        listing = Listing.objects.get(pk=response.data["id"])
        ListingAvailabilityConfirmation.objects.create(listing=listing, confirmed_by=self.owner, is_available=True)
        submit = self.factory.post(f"/listings/{listing.pk}/submit/")
        force_authenticate(submit, user=self.owner)
        submitted = ListingSubmit.as_view()(submit, pk=listing.pk)
        self.assertEqual(submitted.status_code, 200)
        publish = self.factory.post(f"/listings/{listing.pk}/moderate/", {
            "status": Listing.Status.PUBLISHED,
            "moderation_note": "Passed listing review.",
        }, format="json")
        force_authenticate(publish, user=self.staff)
        published = ListingModeration.as_view()(publish, pk=listing.pk)
        self.assertEqual(published.status_code, 200)
        listing.refresh_from_db()
        self.assertEqual(listing.status, Listing.Status.PUBLISHED)

    def test_authorized_agent_can_list_owner_property(self):
        claim = self.claim()
        self.verify_claim(claim)
        auth = self.authorize_agent(claim)
        payload = self.listing_payload(auth)
        request = self.factory.post("/listings/create/", payload, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingCreate.as_view()(request)
        self.assertEqual(response.status_code, 201)
        listing = Listing.objects.get(pk=response.data["id"])
        self.assertEqual(listing.lister_id, self.agent.pk)
        self.assertEqual(listing.authorization_id, auth.pk)
        self.assertTrue(listing.has_current_authority())

    def test_agent_cannot_use_another_agents_authorization(self):
        claim = self.claim()
        self.verify_claim(claim)
        auth = self.authorize_agent(claim)
        payload = self.listing_payload(auth)
        request = self.factory.post("/listings/create/", payload, format="json")
        force_authenticate(request, user=self.member)
        response = ListingCreate.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_public_listing_feed_hides_unpublished(self):
        claim = self.claim()
        self.verify_claim(claim)
        draft = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Draft", price=100)
        request = self.factory.get("/listings/")
        response = PublicListingList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_lister_only_sees_own_listings(self):
        own = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="My draft", price=100)
        another = Listing.objects.create(lister=self.agent, property=self.property, offer_type="rent", headline="Agent draft", price=200)
        request = self.factory.get("/listings/my/")
        force_authenticate(request, user=self.owner)
        response = MyListingList.as_view()(request)
        self.assertEqual([x["id"] for x in response.data], [own.pk])

    def test_lister_cannot_update_another_users_listing(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Owner draft", price=100)
        request = self.factory.patch(f"/listings/{listing.pk}/update/", {"headline": "Hijacked"}, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingUpdate.as_view()(request, pk=listing.pk)
        self.assertEqual(response.status_code, 404)
        listing.refresh_from_db()
        self.assertEqual(listing.headline, "Owner draft")

    def test_lister_cannot_delete_submitted_listing(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Submitted", price=100, status=Listing.Status.SUBMITTED)
        request = self.factory.delete(f"/listings/{listing.pk}/delete/")
        force_authenticate(request, user=self.owner)
        response = ListingDelete.as_view()(request, pk=listing.pk)
        self.assertEqual(response.status_code, 404)

    def test_negative_costs_are_rejected(self):
        listing = Listing(lister=self.owner, property=self.property, offer_type="rent", headline="Negative", price=100, agent_fee_amount=-20)
        with self.assertRaises(ValidationError):
            listing.full_clean()

    def test_upfront_total_calculates_rent_advance_and_fees(self):
        listing = Listing(lister=self.owner, property=self.property, offer_type="rent", headline="Cost calculation", price=1500, billing_period="month", advance_months=12, deposit_amount=500, agent_fee_amount=1000, service_charge_amount=100, costs_disclosed=True)
        self.assertEqual(listing.estimated_upfront_total, 19600)

    def test_listing_requires_moderation_metadata_when_published(self):
        listing = Listing(lister=self.owner, property=self.property, offer_type="rent", headline="Invalid publish", price=100, status=Listing.Status.PUBLISHED)
        with self.assertRaises(ValidationError):
            listing.full_clean()

    def test_only_lister_can_confirm_availability(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Published", price=100, status=Listing.Status.PUBLISHED)
        request = self.factory.post(f"/listings/{listing.pk}/availability/", {"is_available": True, "note": "Confirmed"}, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingAvailabilityConfirm.as_view()(request, pk=listing.pk)
        self.assertEqual(response.status_code, 403)

    def test_lister_confirmation_updates_timestamp_and_history(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Published", price=100, status=Listing.Status.PUBLISHED)
        request = self.factory.post(f"/listings/{listing.pk}/availability/", {"is_available": True, "note": "Available today"}, format="json")
        force_authenticate(request, user=self.owner)
        response = ListingAvailabilityConfirm.as_view()(request, pk=listing.pk)
        self.assertEqual(response.status_code, 201)
        listing.refresh_from_db()
        self.assertIsNotNone(listing.availability_confirmed_at)
        self.assertEqual(listing.availability_confirmations.count(), 1)

    def test_lister_can_pause_listing_by_confirming_unavailable(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Published", price=100, status=Listing.Status.PUBLISHED)
        request = self.factory.post(f"/listings/{listing.pk}/availability/", {"is_available": False, "note": "Already rented"}, format="json")
        force_authenticate(request, user=self.owner)
        response = ListingAvailabilityConfirm.as_view()(request, pk=listing.pk)
        self.assertEqual(response.status_code, 201)
        listing.refresh_from_db()
        self.assertEqual(listing.status, Listing.Status.PAUSED)

    def test_negative_confirmation_invalidates_previous_positive_confirmation(self):
        claim = self.claim()
        self.verify_claim(claim)
        listing = Listing.objects.create(
            lister=self.owner,
            property=self.property,
            offer_type="rent",
            headline="Availability regression",
            price=100,
            costs_disclosed=True,
        )
        ListingAvailabilityConfirmation.objects.create(
            listing=listing, confirmed_by=self.owner, is_available=True,
        )
        listing.submit_for_review()
        listing.moderate(self.staff, Listing.Status.PUBLISHED, "Initial publication.")

        previous_confirmation_at = listing.availability_confirmed_at
        negative_confirmation = ListingAvailabilityConfirmation.objects.create(
            listing=listing, confirmed_by=self.owner, is_available=False,
            note="The property has been rented.",
        )
        listing.refresh_from_db()

        self.assertEqual(listing.status, Listing.Status.PAUSED)
        self.assertEqual(listing.availability_confirmed_at, negative_confirmation.confirmed_at)
        self.assertGreaterEqual(listing.availability_confirmed_at, previous_confirmation_at)
        self.assertFalse(listing.can_publish())
        with self.assertRaises(ValidationError):
            listing.moderate(self.staff, Listing.Status.PUBLISHED, "Attempted republication.")

    def test_agent_listing_published_and_paused_when_ownership_revoked(self):
        claim = self.claim()
        self.verify_claim(claim)
        auth = self.authorize_agent(claim)
        create = self.factory.post("/listings/create/", self.listing_payload(auth), format="json")
        force_authenticate(create, user=self.agent)
        created = ListingCreate.as_view()(create)
        listing = Listing.objects.get(pk=created.data["id"])
        ListingAvailabilityConfirmation.objects.create(listing=listing, confirmed_by=self.agent, is_available=True)
        submit = self.factory.post(f"/listings/{listing.pk}/submit/")
        force_authenticate(submit, user=self.agent)
        self.assertEqual(ListingSubmit.as_view()(submit, pk=listing.pk).status_code, 200)
        publish = self.factory.post(f"/listings/{listing.pk}/moderate/", {"status": "published"}, format="json")
        force_authenticate(publish, user=self.staff)
        self.assertEqual(ListingModeration.as_view()(publish, pk=listing.pk).status_code, 200)
        claim.review(self.staff, PropertyOwnership.Status.REVOKED, "Evidence invalidated.")
        listing.refresh_from_db()
        auth.refresh_from_db()
        self.assertEqual(auth.status, ListingAuthorization.Status.REVOKED)
        self.assertEqual(listing.status, Listing.Status.PAUSED)

    def test_listing_publish_requires_recent_availability_confirmation(self):
        claim = self.claim()
        self.verify_claim(claim)
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="No confirmation", price=100, costs_disclosed=True)
        listing.submit_for_review()
        request = self.factory.post(f"/listings/{listing.pk}/moderate/", {"status": "published"}, format="json")
        force_authenticate(request, user=self.staff)
        response = ListingModeration.as_view()(request, pk=listing.pk)
        self.assertEqual(response.status_code, 400)

    def test_public_feed_excludes_stale_and_expired_offers(self):
        from django.utils import timezone
        from datetime import timedelta

        PropertyOwnership.objects.create(
            property=self.property, claimant=self.owner,
            ownership_type="individual", evidence_type="Test evidence",
            status=PropertyOwnership.Status.VERIFIED,
            reviewed_by=self.staff, reviewed_at=timezone.now(),
        )
        fresh = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Fresh listing", price=100, status=Listing.Status.PUBLISHED, costs_disclosed=True,
            availability_confirmed_at=timezone.now(),
        )
        stale = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Stale listing", price=100, status=Listing.Status.PUBLISHED, costs_disclosed=True,
            availability_confirmed_at=timezone.now() - timedelta(days=31),
        )
        expired = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Expired listing", price=100, status=Listing.Status.PUBLISHED, costs_disclosed=True,
            availability_confirmed_at=timezone.now(), expires_at=timezone.now() - timedelta(days=1),
        )
        request = self.factory.get("/listings/")
        response = PublicListingList.as_view()(request)
        self.assertEqual([item["id"] for item in response.data], [fresh.pk])

    def test_structured_required_tenant_charge_is_in_estimate(self):
        listing = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Structured cost", price=1200, billing_period="month",
            advance_months=6, costs_disclosed=True,
        )
        ListingCharge.objects.create(
            listing=listing, charge_type=ListingCharge.ChargeType.DEPOSIT,
            amount=300, payer=ListingCharge.Payer.TENANT,
            frequency=ListingCharge.Frequency.ONE_TIME, is_required=True,
            created_by=self.owner,
        )
        ListingCharge.objects.create(
            listing=listing, charge_type=ListingCharge.ChargeType.MAINTENANCE,
            amount=900, payer=ListingCharge.Payer.OWNER,
            frequency=ListingCharge.Frequency.ONE_TIME, is_required=True,
            created_by=self.owner,
        )
        self.assertEqual(listing.estimated_upfront_total, 7500)

    def test_unknown_mandatory_upfront_charge_makes_estimate_unknown(self):
        listing = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Unknown charge", price=1000, billing_period="month",
            advance_months=6, costs_disclosed=True,
        )
        ListingCharge.objects.create(
            listing=listing, charge_type=ListingCharge.ChargeType.OTHER,
            amount=None, payer=ListingCharge.Payer.TENANT,
            frequency=ListingCharge.Frequency.ONE_TIME, is_required=True,
            created_by=self.owner,
        )
        self.assertIsNone(listing.estimated_upfront_total)

    def test_optional_upfront_charge_is_not_in_estimate(self):
        listing = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Optional fee", price=1000, billing_period="month",
            advance_months=6, costs_disclosed=True,
        )
        ListingCharge.objects.create(
            listing=listing, charge_type=ListingCharge.ChargeType.OTHER,
            amount=250, payer=ListingCharge.Payer.TENANT,
            frequency=ListingCharge.Frequency.ONE_TIME, is_required=False,
            created_by=self.owner,
        )
        self.assertEqual(listing.estimated_upfront_total, 6000)

    def test_lister_can_add_charge_to_own_draft(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Draft cost", price=100, status=Listing.Status.DRAFT)
        request = self.factory.post(f"/listings/{listing.pk}/charges/", {
            "charge_type": "agent_fee",
            "amount": "450.00",
            "currency": "GHS",
            "payer": "tenant",
            "frequency": "one_time",
            "is_required": True,
            "description": "Agent commission",
        }, format="json")
        force_authenticate(request, user=self.owner)
        response = ListingChargeListCreate.as_view()(request, listing_pk=listing.pk)
        self.assertEqual(response.status_code, 201)
        charge = ListingCharge.objects.get(pk=response.data["id"])
        self.assertEqual(charge.created_by_id, self.owner.pk)
        self.assertEqual(charge.listing_id, listing.pk)

    def test_other_user_cannot_add_charge_to_listing(self):
        listing = Listing.objects.create(lister=self.owner, property=self.property, offer_type="rent", headline="Draft cost", price=100, status=Listing.Status.DRAFT)
        request = self.factory.post(f"/listings/{listing.pk}/charges/", {
            "charge_type": "agent_fee", "amount": "100", "payer": "tenant",
            "frequency": "one_time", "is_required": True,
        }, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingChargeListCreate.as_view()(request, listing_pk=listing.pk)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(listing.charges.count(), 0)

    def test_listing_submission_requires_cost_disclosure(self):
        claim = self.claim()
        self.verify_claim(claim)
        listing = Listing.objects.create(
            lister=self.owner, property=self.property, offer_type="rent",
            headline="Undisclosed charges", price=1000, billing_period="month",
            advance_months=6, costs_disclosed=False,
        )
        with self.assertRaises(ValidationError):
            listing.submit_for_review()
        self.assertEqual(listing.status, Listing.Status.DRAFT)

    def test_only_staff_can_verify_practitioner_license(self):
        license_record = PractitionerLicense.objects.create(
            profile=self.agent,
            license_number="REAC/2026/A/TEST-002",
            license_type=PractitionerLicense.LicenseType.AGENT,
        )
        request = self.factory.patch(f"/licenses/{license_record.pk}/review/", {
            "status": PractitionerLicense.Status.VERIFIED,
            "source_checked_at": timezone.now(),
            "valid_until": timezone.localdate() + timedelta(days=365),
        }, format="json")
        force_authenticate(request, user=self.agent)
        response = PractitionerLicenseReview.as_view()(request, pk=license_record.pk)
        self.assertEqual(response.status_code, 403)

    def test_authorization_approval_requires_current_reac_license(self):
        claim = self.claim()
        self.verify_claim(claim)
        request = self.factory.post("/authorizations/", {
            "property": self.property.pk, "ownership": claim.pk, "authority_type": "agent",
            "evidence_type": "Mandate", "evidence_reference": "private://mandate",
        }, format="json")
        force_authenticate(request, user=self.agent)
        response = ListingAuthorizationCreate.as_view()(request)
        auth = ListingAuthorization.objects.get(pk=response.data["id"])
        review = self.factory.post(f"/authorizations/{auth.pk}/review/", {
            "status": ListingAuthorization.Status.APPROVED,
        }, format="json")
        force_authenticate(review, user=self.staff)
        review_response = ListingAuthorizationReview.as_view()(review, pk=auth.pk)
        self.assertEqual(review_response.status_code, 400)
        auth.refresh_from_db()
        self.assertEqual(auth.status, ListingAuthorization.Status.REQUESTED)

    def test_verified_license_is_explicitly_recorded(self):
        license_record = self.verify_agent_license()
        self.assertTrue(license_record.is_current())
        self.assertEqual(license_record.reviewed_by_id, self.staff.pk)
        self.assertEqual(license_record.license_type, PractitionerLicense.LicenseType.AGENT)

    def test_listing_exposes_masked_current_reac_check(self):
        license_record = self.verify_agent_license()
        listing = Listing.objects.create(
            lister=self.agent, property=self.property, offer_type="rent",
            headline="Agent listed", price=100, costs_disclosed=True,
        )
        serialized = ListingSerializer(listing).data
        self.assertEqual(serialized["lister_license_summary"]["status"], "verified")
        self.assertEqual(serialized["lister_license_summary"]["number_masked"], "••••-001")
        self.assertNotIn(license_record.license_number, str(serialized))

    def test_non_official_license_registry_url_rejected(self):
        serializer = PractitionerLicenseSerializer(data={
            "license_number": "REAC-FAKE-123",
            "license_type": "agent",
            "source_url": "https://fake-registry.example/",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("source_url", serializer.errors)

    def test_expired_license_is_not_current(self):
        license_record = PractitionerLicense.objects.create(
            profile=self.agent,
            license_number="REAC/2026/A/TEST-003",
            license_type=PractitionerLicense.LicenseType.AGENT,
        )
        license_record.review(
            self.staff,
            PractitionerLicense.Status.EXPIRED,
            source_checked_at=timezone.now(),
            valid_until=timezone.localdate() - timedelta(days=1),
        )
