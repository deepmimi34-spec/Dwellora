from rest_framework import serializers
from .models import ProductFeedback


class ProductFeedbackSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    severity = serializers.CharField(read_only=True)
    internal_note = serializers.CharField(read_only=True)
    resolution_summary = serializers.CharField(read_only=True)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if not request or not getattr(request.user, "is_staff", False):
            fields.pop("internal_note", None)
            fields.pop("severity", None)
        return fields

    def validate_page_context(self, value):
        if "?" in value or "#" in value or "://" in value:
            raise serializers.ValidationError("Provide a route only; omit query parameters and full URLs.")
        return value

    class Meta:
        model = ProductFeedback
        fields = ("id", "profile", "category", "title", "description", "page_context", "device_context", "allow_public_idea", "status", "severity", "internal_note", "resolution_summary", "reviewed_by", "reviewed_at", "created_at", "updated_at")
        read_only_fields = ("id", "profile", "status", "severity", "internal_note", "resolution_summary", "reviewed_by", "reviewed_at", "created_at", "updated_at")


class ProductFeedbackTriageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeedback
        fields = ("status", "severity", "internal_note", "resolution_summary")
