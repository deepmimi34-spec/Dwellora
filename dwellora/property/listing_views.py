from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .listing_models import PropertyOwnership, ListingAuthorization, Listing, ListingAvailabilityConfirmation
from .listing_serializers import PropertyOwnershipSerializer, ListingAuthorizationSerializer, ListingSerializer, ListingModerationSerializer, ListingAvailabilityConfirmationSerializer


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
        return Response(PropertyOwnershipSerializer(claim).data)


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
        return Response(ListingAuthorizationSerializer(authorization).data)


class PublicListingList(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Listing.objects.filter(status=Listing.Status.PUBLISHED, availability_confirmed_at__gte=timezone.now() - timedelta(days=30)).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.localdate())).select_related("property", "lister", "authorization")


class PublicListingDetail(generics.RetrieveAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Listing.objects.filter(status=Listing.Status.PUBLISHED, availability_confirmed_at__gte=timezone.now() - timezone.timedelta(days=30)).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.localdate())).select_related("property", "lister", "authorization")


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
        return Response(ListingSerializer(listing).data)


class ListingModeration(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        try:
            listing.moderate(request.user, request.data.get("status"), request.data.get("moderation_note", ""))
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ListingSerializer(listing).data)

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
