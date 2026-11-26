from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ProductFeedback(models.Model):
    class Category(models.TextChoices):
        BUG = "bug", "Bug or broken feature"
        FEATURE = "feature", "Feature request"
        USABILITY = "usability", "Usability or confusing workflow"
        ACCESSIBILITY = "accessibility", "Accessibility"
        DATA_QUALITY = "data_quality", "Listing or information quality"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        TRIAGED = "triaged", "Under review"
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In progress"
        SHIPPED = "shipped", "Shipped"
        DECLINED = "declined", "Declined"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_feedback")
    category = models.CharField(max_length=20, choices=Category.choices)
    title = models.CharField(max_length=140)
    description = models.TextField(max_length=5000)
    page_context = models.CharField(max_length=255, blank=True, help_text="Route or page name only; do not include query tokens or personal data.")
    device_context = models.CharField(max_length=255, blank=True, help_text="Optional context voluntarily supplied by the user.")
    allow_public_idea = models.BooleanField(default=False, help_text="Permission to publish an anonymised idea summary, not account identity.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.NORMAL)
    internal_note = models.TextField(max_length=3000, blank=True)
    resolution_summary = models.TextField(max_length=2000, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="reviewed_product_feedback", null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dwellora_product_feedback"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "category", "created_at"], name="product_feedback_status_idx")]

    def clean(self):
        super().clean()
        if self.status != self.Status.RECEIVED and (not self.reviewed_by_id or not self.reviewed_by.is_staff or not self.reviewed_at):
            raise ValidationError("Feedback status changes require staff triage metadata.")

    def triage(self, staff_user, status, severity=None, internal_note="", resolution_summary=""):
        if not getattr(staff_user, "is_staff", False):
            raise ValidationError("Only staff can triage product feedback.")
        if status not in self.Status.values:
            raise ValidationError("Unsupported feedback status.")
        self.status = status
        if severity is not None:
            if severity not in self.Severity.values:
                raise ValidationError("Unsupported severity.")
            self.severity = severity
        self.internal_note = internal_note
        self.resolution_summary = resolution_summary
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()
        self.full_clean()
        self.save(update_fields=["status", "severity", "internal_note", "resolution_summary", "reviewed_by", "reviewed_at", "updated_at"])
        return self

    def __str__(self):
        return f"{self.category} · {self.title}"
