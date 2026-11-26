from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .listing_models import PropertyOwnership, ListingAuthorization, Listing
from .listing_serializers import PropertyOwnershipSerializer, ListingAuthorizationSerializer, ListingSerializer, ListingModerationSerializer


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
        return Listing.objects.filter(status=Listing.Status.PUBLISHED).select_related("property", "lister", "authorization")


class PublicListingDetail(generics.RetrieveAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Listing.objects.filter(status=Listing.Status.PUBLISHED).select_related("property", "lister", "authorization")


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
