from django.urls import path

from .views import (
    PropertyCreate,
    PropertyDeleteView,
    PropertyDetailView,
    PropertyListView,
    PropertyUpdate,
)
from .listing_views import (
    OwnershipClaimCreate,
    OwnershipClaimList,
    OwnershipClaimReview,
    ListingAuthorizationCreate,
    ListingAuthorizationList,
    ListingAuthorizationReview,
    PractitionerLicenseListCreate,
    PractitionerLicenseReview,
    PublicListingList,
    PublicListingDetail,
    MyListingList,
    ListingCreate,
    ListingUpdate,
    ListingDelete,
    ListingSubmit,
    ListingModeration,
    ListingAvailabilityConfirm,
    ListingChargeListCreate,
    ListingChargeUpdate,
    ListingChargeDelete,
)

urlpatterns = [
    # Legacy physical-property catalogue. Creation and mutation remain staff-only.
    path("property/list/", PropertyListView.as_view(), name="property_list"),
    path("property/create/", PropertyCreate.as_view(), name="property_create"),
    path("property/<int:pk>/detail/", PropertyDetailView.as_view(), name="property_detail"),
    path("property/<int:pk>/update/", PropertyUpdate.as_view(), name="property_update"),
    path("property/<int:pk>/delete/", PropertyDeleteView.as_view(), name="property_delete"),

    # Ownership claims and staff review.
    path("ownership/claims/", OwnershipClaimCreate.as_view(), name="ownership_claim_create"),
    path("ownership/claims/mine/", OwnershipClaimList.as_view(), name="ownership_claim_list"),
    path("ownership/claims/<int:pk>/review/", OwnershipClaimReview.as_view(), name="ownership_claim_review"),

    # Practitioner licence records and staff verification.
    path("licenses/", PractitionerLicenseListCreate.as_view(), name="practitioner_license_list_create"),
    path("licenses/<int:pk>/review/", PractitionerLicenseReview.as_view(), name="practitioner_license_review"),

    # Owner-to-agent / manager authority.
    path("authorizations/", ListingAuthorizationCreate.as_view(), name="listing_authorization_create"),
    path("authorizations/mine/", ListingAuthorizationList.as_view(), name="listing_authorization_list"),
    path("authorizations/<int:pk>/review/", ListingAuthorizationReview.as_view(), name="listing_authorization_review"),

    # Listings: private lister workspace and public marketplace.
    path("listings/create/", ListingCreate.as_view(), name="listing_create"),
    path("listings/my/", MyListingList.as_view(), name="my_listings"),
    path("listings/public/", PublicListingList.as_view(), name="public_listings"),
    path("listings/public/<int:pk>/", PublicListingDetail.as_view(), name="public_listing_detail"),
    path("listings/<int:pk>/update/", ListingUpdate.as_view(), name="listing_update"),
    path("listings/<int:pk>/delete/", ListingDelete.as_view(), name="listing_delete"),
    path("listings/<int:pk>/submit/", ListingSubmit.as_view(), name="listing_submit"),
    path("listings/<int:pk>/moderate/", ListingModeration.as_view(), name="listing_moderate"),
    path("listings/<int:pk>/availability/", ListingAvailabilityConfirm.as_view(), name="listing_availability_confirm"),

    # Itemised charges attached to a lister's draft/rejected listing.
    path("listings/<int:listing_pk>/charges/", ListingChargeListCreate.as_view(), name="listing_charge_list_create"),
    path("charges/<int:pk>/update/", ListingChargeUpdate.as_view(), name="listing_charge_update"),
    path("charges/<int:pk>/delete/", ListingChargeDelete.as_view(), name="listing_charge_delete"),
]
