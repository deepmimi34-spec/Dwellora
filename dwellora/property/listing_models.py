from builtins import property as builtin_property
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .models import Property


class PractitionerLicense(models.Model):
    class LicenseType(models.TextChoices):
        AGENT = "agent", "Real estate agent"
        BROKER = "broker", "Real estate broker"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending check"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"
        EXPIRED = "expired", "Expired"

    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="practitioner_licenses")
    license_number = models.CharField(max_length=64, unique=True)
    license_type = models.CharField(max_length=12, choices=LicenseType.choices)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    valid_until = models.DateField(null=True, blank=True)
    source_checked_at = models.DateTimeField(null=True, blank=True)
    source_url = models.URLField(max_length=300, default="https://reac.gov.gh/public-registry-search/")
    evidence_reference = models.CharField(max_length=255, blank=True, help_text="Private evidence-storage reference, not a public document URL.")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="reviewed_practitioner_licenses", null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "practitioner_license"
        ordering = ["-reviewed_at", "-created_at"]

    def clean(self):
        super().clean()
        if self.status == self.Status.VERIFIED:
            if not self.reviewed_by_id or not self.reviewed_by.is_staff or not self.reviewed_at:
                raise ValidationError("Verified licence records require staff review metadata.")
            if not self.source_checked_at or not self.valid_until:
                raise ValidationError("Verified licence requires a registry-check date and expiry date.")
            if self.valid_until < timezone.localdate():
                raise ValidationError("An expired licence cannot be marked verified.")

    def is_current(self):
        return self.status == self.Status.VERIFIED and self.valid_until is not None and self.valid_until >= timezone.localdate()

    def review(self, staff_user, status, source_checked_at=None, valid_until=None, note=""):
        if not getattr(staff_user, "is_staff", False):
            raise ValidationError("Only staff may verify practitioner licences.")
        if status not in (self.Status.VERIFIED, self.Status.REJECTED, self.Status.SUSPENDED, self.Status.EXPIRED):
            raise ValidationError("Unsupported licence review status.")
        self.status = status
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()
        if source_checked_at is not None:
            self.source_checked_at = source_checked_at
        if valid_until is not None:
            self.valid_until = valid_until
        self.review_note = note
        self.full_clean()
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "source_checked_at", "valid_until", "review_note"])
        if status != self.Status.VERIFIED:
            for authorization in ListingAuthorization.objects.filter(lister=self.profile, status=ListingAuthorization.Status.APPROVED):
                if not PractitionerLicense.objects.filter(profile=self.profile, status=self.Status.VERIFIED, valid_until__gte=timezone.localdate()).exclude(pk=self.pk).exists():
                    authorization.review(staff_user, ListingAuthorization.Status.REVOKED, "Practitioner licence is no longer current.")
        return self


class PropertyOwnership(models.Model):
    class Status(models.TextChoices):
        CLAIMED = "claimed", "Claim submitted"
        UNDER_REVIEW = "under_review", "Under review"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        REVOKED = "revoked", "Revoked"

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="ownership_claims")
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="property_ownership_claims")
    ownership_type = models.CharField(max_length=32, choices=[("individual", "Individual"), ("company_representative", "Company representative")], default="individual")
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
        if status == self.Status.REVOKED:
            for direct_listing in self.property.listings.filter(lister=self.claimant, status=Listing.Status.PUBLISHED):
                direct_listing.moderate(staff_user, Listing.Status.PAUSED, "Underlying ownership was revoked.")
            for authorization in self.authorizations.filter(status=ListingAuthorization.Status.APPROVED):
                authorization.review(staff_user, ListingAuthorization.Status.REVOKED, "Underlying ownership was revoked.")
                for listing in authorization.listings.filter(status=Listing.Status.PUBLISHED):
                    listing.moderate(staff_user, Listing.Status.PAUSED, "Underlying ownership was revoked.")
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
            if self.ownership.claimant_id == self.lister_id:
                raise ValidationError("An owner should use a direct listing; authorization is for another lister.")
            if not self.evidence_type.strip():
                raise ValidationError("Approved authorization must record its evidence type.")
            if self.ownership.status != PropertyOwnership.Status.VERIFIED:
                raise ValidationError("Only verified ownership can support an authorization.")
            if not PractitionerLicense.objects.filter(
                profile=self.lister,
                status=PractitionerLicense.Status.VERIFIED,
                valid_until__gte=timezone.localdate(),
            ).exists():
                raise ValidationError("The lister must have a current REAC licence verified by staff.")
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
        if status == self.Status.REVOKED:
            for listing in self.listings.filter(status=Listing.Status.PUBLISHED):
                listing.moderate(staff_user, Listing.Status.PAUSED, "Listing authorization was revoked.")
        return self

    def is_current(self):
        today = timezone.localdate()
        license_is_current = PractitionerLicense.objects.filter(
            profile=self.lister,
            status=PractitionerLicense.Status.VERIFIED,
            valid_until__gte=today,
        ).exists()
        return (
            self.status == self.Status.APPROVED
            and self.ownership.status == PropertyOwnership.Status.VERIFIED
            and license_is_current
            and (not self.valid_from or self.valid_from <= today)
            and (not self.valid_until or self.valid_until >= today)
        )


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
    costs_disclosed = models.BooleanField(default=False, help_text="Lister confirms all known upfront and recurring charges have been disclosed.")
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
        # Unsaved listings have no reverse confirmation relation to query.
        if not self.pk:
            return False
        latest_confirmation = self.availability_confirmations.order_by("-confirmed_at", "-pk").first()
        confirmed_recently = (
            latest_confirmation is not None
            and latest_confirmation.is_available
            and latest_confirmation.confirmed_at >= timezone.now() - timedelta(days=30)
        )
        return (
            self.has_current_authority()
            and self.property.is_property_complete()
            and bool(self.headline and self.price >= 0)
            and self.costs_disclosed
            and confirmed_recently
        )

    def submit_for_review(self):
        if not self.has_current_authority():
            raise ValidationError("Verified ownership or approved listing authority is required before submission.")
        if not self.costs_disclosed:
            raise ValidationError("Complete the cost disclosure before submitting this listing.")
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

    @builtin_property
    def estimated_upfront_total(self):
        if not self.costs_disclosed:
            return None
        if self.offer_type == self.OfferType.SHORT_STAY and self.billing_period == "night":
            return None
        if self.offer_type == self.OfferType.RENT and self.billing_period == "month" and not self.advance_months:
            return None
        base = self.price * self.advance_months if self.offer_type == self.OfferType.RENT and self.billing_period == "month" else self.price
        total = base + self.deposit_amount + self.agent_fee_amount + self.viewing_fee_amount + self.service_charge_amount + self.other_fees_amount
        payer = "tenant" if self.offer_type == self.OfferType.RENT else "buyer"
        if self.pk:
            charges = self.charges.all()
        else:
            charges = []
        for charge in charges:
            if charge.frequency != ListingCharge.Frequency.ONE_TIME:
                continue
            if charge.is_required is False:
                continue
            if charge.is_required is None:
                if charge.payer in (payer, "shared", "not_specified"):
                    return None
                continue
            if charge.payer in ("shared", "not_specified"):
                return None
            if charge.payer == payer:
                if charge.amount is None:
                    return None
                total += charge.amount
        return total

    def availability_freshness(self):
        if not self.availability_confirmed_at:
            return "not_confirmed"
        if self.availability_confirmed_at < timezone.now() - timedelta(days=30):
            return "stale"
        return "fresh"



class ListingAvailabilityConfirmation(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="availability_confirmations")
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listing_availability_confirmations")
    is_available = models.BooleanField()
    note = models.CharField(max_length=500, blank=True)
    confirmed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "listing_availability_confirmation"
        ordering = ["-confirmed_at"]

    def clean(self):
        super().clean()
        if self.listing_id and self.confirmed_by_id != self.listing.lister_id and not self.confirmed_by.is_staff:
            raise ValidationError("Only the lister or staff can confirm listing availability.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # Every confirmation supersedes the previous availability state.
        self.listing.availability_confirmed_at = self.confirmed_at
        update_fields = ["availability_confirmed_at", "updated_at"]
        if not self.is_available and self.listing.status == Listing.Status.PUBLISHED:
            self.listing.status = Listing.Status.PAUSED
            update_fields.append("status")
        self.listing.save(update_fields=update_fields)

class ListingCharge(models.Model):
    class ChargeType(models.TextChoices):
        DEPOSIT = "deposit", "Security deposit"
        AGENT_FEE = "agent_fee", "Agent commission"
        VIEWING_FEE = "viewing_fee", "Viewing fee"
        SERVICE_CHARGE = "service_charge", "Service charge"
        UTILITIES = "utilities", "Utilities"
        MAINTENANCE = "maintenance", "Maintenance"
        OTHER = "other", "Other"

    class Payer(models.TextChoices):
        TENANT = "tenant", "Tenant"
        BUYER = "buyer", "Buyer"
        LISTER = "lister", "Lister"
        OWNER = "owner", "Property owner"
        SHARED = "shared", "Shared"
        NOT_SPECIFIED = "not_specified", "Not specified"

    class Frequency(models.TextChoices):
        ONE_TIME = "one_time", "One-time"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"
        OTHER = "other", "Other"

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="charges")
    charge_type = models.CharField(max_length=20, choices=ChargeType.choices, default=ChargeType.OTHER)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="GHS")
    payer = models.CharField(max_length=20, choices=Payer.choices, default=Payer.NOT_SPECIFIED)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.ONE_TIME)
    is_required = models.BooleanField(null=True, blank=True, help_text="Unknown is different from optional.")
    description = models.CharField(max_length=300, blank=True)
    source_note = models.CharField(max_length=300, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_listing_charges")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "listing_charge"
        ordering = ["charge_type", "created_at"]

    def clean(self):
        super().clean()
        if self.amount is not None and self.amount < 0:
            raise ValidationError("Charge amount cannot be negative.")

    def __str__(self):
        amount_label = "Not provided" if self.amount is None else f"{self.currency} {self.amount}"
        return f"{self.listing.headline} · {self.charge_type} · {amount_label}"
