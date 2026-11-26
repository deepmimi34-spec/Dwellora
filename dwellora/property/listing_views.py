from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .listing_models import PractitionerLicense, PropertyOwnership, ListingAuthorization, Listing, ListingAvailabilityConfirmation, ListingCharge
from .listing_serializers import PractitionerLicenseSerializer, PractitionerLicenseReviewSerializer, PropertyOwnershipSerializer, ListingAuthorizationSerializer, ListingSerializer, ListingModerationSerializer, ListingAvailabilityConfirmationSerializer, ListingChargeSerializer


class OwnershipClaimCreate(generics.CreateAPIView):
    serializer_class = PropertyOwnershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(claimant=self.request.user)


class OwnershipClaimList(generics.ListAPIView):
    serializer_class = PropertyOwnershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PropertyOwnership.objects.select_related("property", "claimant", "reviewed_by")
        return queryset if self.request.user.is_staff else queryset.filter(claimant=self.request.user)


class OwnershipClaimReview(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        claim = get_object_or_404(PropertyOwnership, pk=pk)
        try:
            claim.review(request.user, request.data.get("status"), request.data.get("review_note", ""))
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PropertyOwnershipSerializer(claim, context={"request": request}).data)


class ListingAuthorizationCreate(generics.CreateAPIView):
    serializer_class = ListingAuthorizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(lister=self.request.user)


class ListingAuthorizationList(generics.ListAPIView):
    serializer_class = ListingAuthorizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ListingAuthorization.objects.select_related("property", "ownership", "lister", "reviewed_by")
        return qs if self.request.user.is_staff else qs.filter(lister=self.request.user)


class ListingAuthorizationReview(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        authorization = get_object_or_404(ListingAuthorization, pk=pk)
        try:
            authorization.review(request.user, request.data.get("status"), request.data.get("review_note", ""))
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ListingAuthorizationSerializer(authorization, context={"request": request}).data)


def public_listing_queryset():
    today = timezone.localdate()
    return Listing.objects.filter(
        status=Listing.Status.PUBLISHED,
        costs_disclosed=True,
        availability_confirmed_at__gte=timezone.now() - timedelta(days=30),
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).filter(
        Q(
            authorization__isnull=True,
            property__ownership_claims__claimant=F("lister"),
            property__ownership_claims__status=PropertyOwnership.Status.VERIFIED,
        )
        | Q(
            authorization__status=ListingAuthorization.Status.APPROVED,
            authorization__ownership__status=PropertyOwnership.Status.VERIFIED,
            authorization__lister=F("lister"),
            authorization__lister__practitioner_licenses__status=PractitionerLicense.Status.VERIFIED,
            authorization__lister__practitioner_licenses__valid_until__gte=today,
        )
    ).filter(
        Q(authorization__valid_from__isnull=True) | Q(authorization__valid_from__lte=today)
    ).filter(
        Q(authorization__valid_until__isnull=True) | Q(authorization__valid_until__gte=today)
    ).select_related("property", "lister", "authorization", "authorization__ownership").prefetch_related("lister__practitioner_licenses").distinct()


class PublicListingList(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return public_listing_queryset()


class PublicListingDetail(generics.RetrieveAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    queryset = public_listing_queryset()


class MyListingList(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(lister=self.request.user).select_related("property", "authorization")


class ListingCreate(generics.CreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListingUpdate(generics.UpdateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(lister=self.request.user, status__in=[Listing.Status.DRAFT, Listing.Status.REJECTED])


class ListingDelete(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(lister=self.request.user, status=Listing.Status.DRAFT)


class ListingSubmit(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk, lister=request.user)
        try:
            listing.submit_for_review()
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ListingSerializer(listing, context={"request": request}).data)


class ListingModeration(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        try:
            listing.moderate(request.user, request.data.get("status"), request.data.get("moderation_note", ""))
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ListingSerializer(listing, context={"request": request}).data)

class ListingAvailabilityConfirm(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.lister_id != request.user.pk and not request.user.is_staff:
            return Response({"detail": "Only the listing owner or staff can confirm availability."}, status=status.HTTP_403_FORBIDDEN)
        if listing.status not in (Listing.Status.DRAFT, Listing.Status.SUBMITTED, Listing.Status.PUBLISHED, Listing.Status.PAUSED):
            return Response({"detail": "Availability can only be confirmed for published or paused listings."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ListingAvailabilityConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation = serializer.save(listing=listing, confirmed_by=request.user)
        return Response(ListingAvailabilityConfirmationSerializer(confirmation).data, status=status.HTTP_201_CREATED)

class ListingChargeListCreate(generics.ListCreateAPIView):
    serializer_class = ListingChargeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        listing = get_object_or_404(Listing, pk=self.kwargs["listing_pk"])
        if listing.lister_id != self.request.user.pk and not self.request.user.is_staff:
            return ListingCharge.objects.none()
        return ListingCharge.objects.filter(listing=listing).select_related("listing", "created_by")

    def perform_create(self, serializer):
        listing = get_object_or_404(Listing, pk=self.kwargs["listing_pk"], lister=self.request.user, status__in=[Listing.Status.DRAFT, Listing.Status.REJECTED])
        serializer.save(listing=listing, created_by=self.request.user)


class ListingChargeUpdate(generics.UpdateAPIView):
    serializer_class = ListingChargeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ListingCharge.objects.filter(listing__lister=self.request.user, listing__status__in=[Listing.Status.DRAFT, Listing.Status.REJECTED])


class ListingChargeDelete(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ListingCharge.objects.filter(listing__lister=self.request.user, listing__status=Listing.Status.DRAFT)

class PractitionerLicenseListCreate(generics.ListCreateAPIView):
    serializer_class = PractitionerLicenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = PractitionerLicense.objects.select_related("profile", "reviewed_by")
        return qs if self.request.user.is_staff else qs.filter(profile=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user)


class PractitionerLicenseReview(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        license_record = get_object_or_404(PractitionerLicense, pk=pk)
        serializer = PractitionerLicenseReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        try:
            license_record.review(
                request.user,
                values["status"],
                values.get("source_checked_at"),
                values.get("valid_until"),
                values.get("review_note", ""),
            )
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PractitionerLicenseSerializer(license_record, context={"request": request}).data)
