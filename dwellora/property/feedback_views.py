from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PropertyComment, PropertyContentReport, PropertyInteraction, PropertyReview
from .feedback_serializers import (
    PropertyCommentModerationSerializer,
    PropertyCommentSerializer,
    PropertyContentReportSerializer,
    PropertyContentReportStatusSerializer,
    PropertyInteractionSerializer,
    PropertyInteractionStatusSerializer,
    PropertyReviewModerationSerializer,
    PropertyReviewSerializer,
)


class PropertyReviewList(generics.ListAPIView):
    serializer_class = PropertyReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return PropertyReview.objects.filter(
            interaction__property_id=self.kwargs['property_pk'],
            moderation_status=PropertyReview.ModerationStatus.PUBLISHED,
        ).select_related('interaction', 'interaction__profile', 'interaction__property')


class PropertyReviewCreate(generics.CreateAPIView):
    serializer_class = PropertyReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        interaction = serializer.validated_data['interaction']
        if interaction.property_id != self.kwargs['property_pk']:
            raise serializers.ValidationError(
                'The verified interaction does not belong to this property.'
            )
        serializer.save()


class PropertyReviewModerationUpdate(generics.UpdateAPIView):
    queryset = PropertyReview.objects.all()
    serializer_class = PropertyReviewModerationSerializer
    permission_classes = [permissions.IsAdminUser]


class PropertyCommentList(generics.ListAPIView):
    serializer_class = PropertyCommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = PropertyComment.objects.filter(
            property_id=self.kwargs['property_pk'],
        ).select_related('author', 'property', 'parent')

        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(moderation_status=PropertyComment.ModerationStatus.PUBLISHED)
                | Q(author=self.request.user)
            )
        else:
            queryset = queryset.filter(
                moderation_status=PropertyComment.ModerationStatus.PUBLISHED
            )

        return queryset.order_by('created_at')


class PropertyCommentCreate(generics.CreateAPIView):
    serializer_class = PropertyCommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class PropertyCommentModerationUpdate(generics.UpdateAPIView):
    queryset = PropertyComment.objects.all()
    serializer_class = PropertyCommentModerationSerializer
    permission_classes = [permissions.IsAdminUser]


class PropertyCommentDelete(generics.DestroyAPIView):
    serializer_class = PropertyCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PropertyComment.objects.all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(
            author=self.request.user,
            moderation_status=PropertyComment.ModerationStatus.PENDING,
        )


class PropertyInteractionListCreate(generics.ListCreateAPIView):
    serializer_class = PropertyInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PropertyInteraction.objects.select_related(
            'property', 'profile', 'verified_by'
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(profile=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user)


class PropertyInteractionStatusUpdate(generics.UpdateAPIView):
    queryset = PropertyInteraction.objects.all()
    serializer_class = PropertyInteractionStatusSerializer
    permission_classes = [permissions.IsAdminUser]


class PropertyInteractionVerify(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        interaction = get_object_or_404(PropertyInteraction, pk=pk)
        try:
            interaction.mark_verified(request.user)
        except DjangoValidationError as error:
            return Response(
                {'detail': error.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            PropertyInteractionSerializer(interaction).data,
            status=status.HTTP_200_OK,
        )


class PropertyContentReportListCreate(generics.ListCreateAPIView):
    serializer_class = PropertyContentReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PropertyContentReport.objects.select_related(
            'reporter', 'review', 'comment', 'reviewed_by'
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(reporter=self.request.user)

class PropertyContentReportStatusUpdate(generics.UpdateAPIView):
    queryset = PropertyContentReport.objects.all()
    serializer_class = PropertyContentReportStatusSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        from django.utils import timezone

        serializer.save(
            reviewed_by=self.request.user,
            reviewed_at=timezone.now(),
        )
