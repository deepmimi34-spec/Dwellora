from django.db.models import Q
from rest_framework import generics, permissions, serializers

from .models import PropertyComment, PropertyReview
from .feedback_serializers import (
    PropertyCommentModerationSerializer,
    PropertyCommentSerializer,
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
