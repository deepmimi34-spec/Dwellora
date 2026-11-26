from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from property.models import Property
from property.listing_models import PropertyOwnership, ListingAuthorization, Listing
from property.listing_views import (
    OwnershipClaimCreate, OwnershipClaimReview,
    ListingAuthorizationCreate, ListingAuthorizationReview,
    ListingCreate, ListingSubmit, ListingModeration,
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

    def authorize_agent(self, claim):
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

    def test_owner_can_create_draft_but_cannot_publish_unverified_claim(self):
        self.claim()
        request = self.factory.post("/listings/create/", self.listing_payload(), format="json")
        force_authenticate(request, user=self.owner)
        response = ListingCreate.as_view()(request)
        self.assertEqual(response.status_code, 201)
        listing = Listing.objects.get(pk=response.data["id"])
        self.assertEqual(listing.lister_id, self.owner.pk)
        self.assertEqual(listing.status, Listing.Status.DRAFT)
        submit = self.factory.post(f"/listings/{listing.pk}/submit/")
        force_authenticate(submit, user=self.owner)
        submit_response = ListingSubmit.as_view()(submit, pk=listing.pk)
        self.assertEqual(submit_response.status_code, 400)

    def test_verified_owner_can_submit_and_staff_publish(self):
        claim = self.claim()
        self.verify_claim(claim)
        request = self.factory.post("/listings/create/", self.listing_payload(), format="json")
        force_authenticate(request, user=self.owner)
        response = ListingCreate.as_view()(request)
        listing = Listing.objects.get(pk=response.data["id"])
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
        listing = Listing(lister=self.owner, property=self.property, offer_type="rent", headline="Cost calculation", price=1500, billing_period="month", advance_months=12, deposit_amount=500, agent_fee_amount=1000, service_charge_amount=100)
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
