from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .models import Property


class PropertyOwnership(models.Model):
    class Status(models.TextChoices):
        CLAIMED = "claimed", "Claim submitted"
        UNDER_REVIEW = "under_review", "Under review"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        REVOKED = "revoked", "Revoked"

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="ownership_claims")
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="property_ownership_claims")
    ownership_type = models.CharField(max_length=20, choices=[("individual", "Individual"), ("company_representative", "Company representative")], default="individual")
    evidence_type = models.CharField(max_length=80, blank=True, help_text="Evidence category only; never place sensitive document contents here.")
    evidence_reference = models.CharField(max_length=255, blank=True, help_text="Private storage reference. Do not use a public URL.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CLAIMED)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="reviewed_ownership_claims", null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(max_length=1000, blank=True)

    class Meta:
        db_table = "property_ownership"
        ordering = ["-submitted_at"]
        constraints = [models.UniqueConstraint(fields=["property", "claimant"], name="unique_property_claimant")]

    def clean(self):
        super().clean()
        if self.status == self.Status.VERIFIED:
            if not self.reviewed_by_id or not self.reviewed_by.is_staff or not self.reviewed_at:
                raise ValidationError("Verified ownership requires staff review metadata.")
        elif self.reviewed_by_id and not self.reviewed_at:
            raise ValidationError("Review metadata must include a timestamp.")

    def review(self, staff_user, status, note=""):
        if not getattr(staff_user, "is_staff", False):
            raise ValidationError("Only staff may review ownership claims.")
        if status not in (self.Status.VERIFIED, self.Status.REJECTED, self.Status.REVOKED):
            raise ValidationError("Unsupported review status.")
        self.status = status
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()
        self.review_note = note
        self.full_clean()
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note"])
        return self


class ListingAuthorization(models.Model):
    class AuthorityType(models.TextChoices):
        OWNER = "owner", "Owner listing"
        AGENT = "agent", "Authorised agent"
        MANAGER = "manager", "Property manager"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REVOKED = "revoked", "Revoked"

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="listing_authorizations")
    ownership = models.ForeignKey(PropertyOwnership, on_delete=models.PROTECT, related_name="authorizations")
    lister = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listing_authorizations")
    authority_type = models.CharField(max_length=20, choices=AuthorityType.choices)
    evidence_type = models.CharField(max_length=80, blank=True)
    evidence_reference = models.CharField(max_length=255, blank=True, help_text="Private storage reference only.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="reviewed_listing_authorizations", null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(max_length=1000, blank=True)

    class Meta:
        db_table = "listing_authorization"
        ordering = ["-id"]

    def clean(self):
        super().clean()
        if self.ownership_id and self.ownership.property_id != self.property_id:
            raise ValidationError("Authorization and ownership must refer to the same property.")
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValidationError("Authorization end date cannot precede its start date.")
        if self.status == self.Status.APPROVED:
            if self.ownership.status != PropertyOwnership.Status.VERIFIED:
                raise ValidationError("Only verified ownership can support an authorization.")
            if not self.reviewed_by_id or not self.reviewed_by.is_staff or not self.reviewed_at:
                raise ValidationError("Approved authorization requires staff review metadata.")

    def review(self, staff_user, status, note=""):
        if not getattr(staff_user, "is_staff", False):
            raise ValidationError("Only staff may review listing authorization.")
        if status not in (self.Status.APPROVED, self.Status.REJECTED, self.Status.REVOKED):
            raise ValidationError("Unsupported authorization review status.")
        self.status = status
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()
        self.review_note = note
        self.full_clean()
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note"])
        return self

    def is_current(self):
        today = timezone.localdate()
        return self.status == self.Status.APPROVED and self.ownership.status == PropertyOwnership.Status.VERIFIED and (not self.valid_from or self.valid_from <= today) and (not self.valid_until or self.valid_until >= today)


class Listing(models.Model):
    class OfferType(models.TextChoices):
        RENT = "rent", "For rent"
        SALE = "sale", "For sale"
        SHORT_STAY = "short_stay", "Short stay"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted for review"
        PUBLISHED = "published", "Published"
        PAUSED = "paused", "Paused"
        RENTED = "rented", "Rented"
        SOLD = "sold", "Sold"
        EXPIRED = "expired", "Expired"
        REJECTED = "rejected", "Rejected"
        REMOVED = "removed", "Removed"

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="listings")
    lister = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="property_listings")
    authorization = models.ForeignKey(ListingAuthorization, on_delete=models.PROTECT, related_name="listings", null=True, blank=True)
    offer_type = models.CharField(max_length=20, choices=OfferType.choices)
    headline = models.CharField(max_length=160)
    description = models.TextField(max_length=5000, blank=True)
    unit_label = models.CharField(max_length=80, blank=True, help_text="Optional unit identifier, such as Block B, Flat 3, or Room 12.")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")
    billing_period = models.CharField(max_length=20, choices=[("total", "Total price"), ("night", "Per night"), ("month", "Per month"), ("year", "Per year")], default="total")
    advance_months = models.PositiveSmallIntegerField(null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    agent_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    viewing_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_charge_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_fees_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_fees_description = models.CharField(max_length=255, blank=True)
    availability_confirmed_at = models.DateTimeField(null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    moderation_note = models.TextField(max_length=1000, blank=True)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="moderated_listings", null=True, blank=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "property_listing"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "offer_type", "created_at"], name="listing_status_offer_idx")]

    def clean(self):
        super().clean()
        if self.price < 0 or any(value < 0 for value in [self.deposit_amount, self.agent_fee_amount, self.viewing_fee_amount, self.service_charge_amount, self.other_fees_amount]):
            raise ValidationError("Prices and fees cannot be negative.")
        if self.expires_at and self.published_at and self.expires_at < self.published_at:
            raise ValidationError("Listing expiry must be after publication.")
        if self.authorization_id:
            if self.authorization.property_id != self.property_id:
                raise ValidationError("Listing authorization must match the property.")
            if self.authorization.lister_id != self.lister_id:
                raise ValidationError("Listing lister must match the authorization.")
        if self.status == self.Status.PUBLISHED and not self.can_publish():
            raise ValidationError("Only a lister with verified, current authority may publish.")
        if self.status in (self.Status.PUBLISHED, self.Status.REJECTED, self.Status.REMOVED):
            if not self.moderated_by_id or not self.moderated_by.is_staff or not self.moderated_at:
                raise ValidationError("Moderated listing states require staff review metadata.")

    def has_current_authority(self):
        if self.authorization_id:
            return self.authorization.is_current()
        return PropertyOwnership.objects.filter(property=self.property, claimant=self.lister, status=PropertyOwnership.Status.VERIFIED).exists()

    def can_publish(self):
        return self.has_current_authority() and self.property.is_property_complete() and bool(self.headline and self.price >= 0)

    def submit_for_review(self):
        if not self.has_current_authority():
            raise ValidationError("Verified ownership or approved listing authority is required before submission.")
        self.status = self.Status.SUBMITTED
        self.full_clean()
        self.save(update_fields=["status", "updated_at"])

    def moderate(self, staff_user, status, note=""):
        if not getattr(staff_user, "is_staff", False):
            raise ValidationError("Only staff may moderate listings.")
        if status not in (self.Status.PUBLISHED, self.Status.REJECTED, self.Status.REMOVED, self.Status.PAUSED):
            raise ValidationError("Unsupported moderation status.")
        if status == self.Status.PUBLISHED and not self.can_publish():
            raise ValidationError("The listing does not meet publication requirements.")
        self.status = status
        self.moderated_by = staff_user
        self.moderated_at = timezone.now()
        self.moderation_note = note
        if status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        self.full_clean()
        self.save(update_fields=["status", "moderated_by", "moderated_at", "moderation_note", "published_at", "updated_at"])
        return self

    @property
    def estimated_upfront_total(self):
        base = self.price * self.advance_months if self.billing_period == "month" and self.advance_months else self.price
        return base + self.deposit_amount + self.agent_fee_amount + self.viewing_fee_amount + self.service_charge_amount + self.other_fees_amount

    def __str__(self):
        return f"{self.headline} · {self.property.title}"
