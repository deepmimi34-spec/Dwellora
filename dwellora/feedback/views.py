from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import ProductFeedback
from .serializers import ProductFeedbackSerializer, ProductFeedbackTriageSerializer


class ProductFeedbackListCreate(generics.ListCreateAPIView):
    serializer_class = ProductFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ProductFeedback.objects.select_related("profile", "reviewed_by")
        return qs if self.request.user.is_staff else qs.filter(profile=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user)


class ProductFeedbackTriage(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        feedback = get_object_or_404(ProductFeedback, pk=pk)
        serializer = ProductFeedbackTriageSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        try:
            feedback.triage(
                request.user,
                values.get("status", feedback.status),
                values.get("severity"),
                values.get("internal_note", feedback.internal_note),
                values.get("resolution_summary", feedback.resolution_summary),
            )
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ProductFeedbackSerializer(feedback).data)
