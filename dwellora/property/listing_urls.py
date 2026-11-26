from django.urls import path
from .listing_views import (
    OwnershipClaimCreate, OwnershipClaimList, OwnershipClaimReview,
    ListingAuthorizationCreate, ListingAuthorizationList, ListingAuthorizationReview,
    PublicListingList, PublicListingDetail, MyListingList, ListingCreate,
    ListingUpdate, ListingDelete, ListingSubmit, ListingModeration, ListingAvailabilityConfirm,
)

urlpatterns = [
    path("ownership/claims/", OwnershipClaimCreate.as_view(), name="ownership-claim-create"),
    path("ownership/my-claims/", OwnershipClaimList.as_view(), name="ownership-claim-list"),
    path("ownership/claims/<int:pk>/review/", OwnershipClaimReview.as_view(), name="ownership-claim-review"),
    path("authorizations/", ListingAuthorizationCreate.as_view(), name="listing-authorization-create"),
    path("authorizations/my/", ListingAuthorizationList.as_view(), name="listing-authorization-list"),
    path("authorizations/<int:pk>/review/", ListingAuthorizationReview.as_view(), name="listing-authorization-review"),
    path("listings/", PublicListingList.as_view(), name="public-listings"),
    path("listings/<int:pk>/", PublicListingDetail.as_view(), name="public-listing-detail"),
    path("listings/my/", MyListingList.as_view(), name="my-listings"),
    path("listings/create/", ListingCreate.as_view(), name="listing-create"),
    path("listings/<int:pk>/update/", ListingUpdate.as_view(), name="listing-update"),
    path("listings/<int:pk>/delete/", ListingDelete.as_view(), name="listing-delete"),
    path("listings/<int:pk>/submit/", ListingSubmit.as_view(), name="listing-submit"),
    path("listings/<int:pk>/availability/", ListingAvailabilityConfirm.as_view(), name="listing-availability-confirm"),
    path("listings/<int:pk>/moderate/", ListingModeration.as_view(), name="listing-moderation"),
]
