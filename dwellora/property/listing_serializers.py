from rest_framework import serializers
from .listing_models import PractitionerLicense, PropertyOwnership, ListingAuthorization, Listing, ListingAvailabilityConfirmation, ListingCharge
from .models import Property



class PractitionerLicenseSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True)
    review_note = serializers.CharField(read_only=True)

    def validate_source_url(self, value):
        if not value.startswith("https://reac.gov.gh/"):
            raise serializers.ValidationError("Registry checks must reference the official REAC website.")
        return value

    class Meta:
        model = PractitionerLicense
        fields = ("id", "profile", "license_number", "license_type", "status", "valid_until", "source_checked_at", "source_url", "evidence_reference", "reviewed_by", "reviewed_at", "review_note", "created_at")
        read_only_fields = ("id", "profile", "status", "reviewed_by", "reviewed_at", "review_note", "created_at")


class PractitionerLicenseReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=PractitionerLicense.Status.choices)
    source_checked_at = serializers.DateTimeField(required=False)
    valid_until = serializers.DateField(required=False)
    review_note = serializers.CharField(required=False, max_length=1000, allow_blank=True)

class PropertyOwnershipSerializer(serializers.ModelSerializer):
    claimant = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True)
    review_note = serializers.CharField(read_only=True)

    class Meta:
        model = PropertyOwnership
        fields = ("id", "property", "claimant", "ownership_type", "evidence_type", "evidence_reference", "status", "submitted_at", "reviewed_by", "reviewed_at", "review_note")
        read_only_fields = ("id", "claimant", "status", "submitted_at", "reviewed_by", "reviewed_at", "review_note")

    def validate(self, attrs):
        request = self.context["request"]
        property_obj = attrs["property"]
        if PropertyOwnership.objects.filter(property=property_obj, claimant=request.user).exists():
            raise serializers.ValidationError("You already have an ownership claim for this property.")
        return attrs


class ListingAuthorizationSerializer(serializers.ModelSerializer):
    lister = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True)
    review_note = serializers.CharField(read_only=True)

    class Meta:
        model = ListingAuthorization
        fields = ("id", "property", "ownership", "lister", "authority_type", "evidence_type", "evidence_reference", "status", "valid_from", "valid_until", "reviewed_by", "reviewed_at", "review_note")
        read_only_fields = ("id", "lister", "status", "reviewed_by", "reviewed_at", "review_note")

    def validate(self, attrs):
        request = self.context["request"]
        ownership = attrs["ownership"]
        if ownership.claimant_id == request.user.pk:
            raise serializers.ValidationError("Property owners should create their own listing, not an agent authorization.")
        if ownership.property_id != attrs["property"].pk:
            raise serializers.ValidationError("The ownership claim must match the property.")
        if ownership.status != PropertyOwnership.Status.VERIFIED:
            raise serializers.ValidationError("Authorization requests require verified ownership.")
        if ListingAuthorization.objects.filter(property=attrs["property"], lister=request.user, status__in=[ListingAuthorization.Status.REQUESTED, ListingAuthorization.Status.APPROVED]).exists():
            raise serializers.ValidationError("An active authorization request already exists for this property.")
        return attrs



class ListingChargeSerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ListingCharge
        fields = ("id", "listing", "charge_type", "amount", "currency", "payer", "frequency", "is_required", "description", "source_note", "created_by", "created_at", "updated_at")
        read_only_fields = ("id", "listing", "created_by", "created_at", "updated_at")

    def validate_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Charge amount cannot be negative.")
        return value

class ListingSerializer(serializers.ModelSerializer):
    charges = ListingChargeSerializer(many=True, read_only=True)\n    lister_license_summary = serializers.SerializerMethodField()
    lister = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    property_title = serializers.CharField(source="property.title", read_only=True)
    estimated_upfront_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, allow_null=True)
    availability_freshness = serializers.CharField(source="availability_freshness", read_only=True)
    moderated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    moderated_at = serializers.DateTimeField(read_only=True)
    moderation_note = serializers.CharField(read_only=True)


    def get_lister_license_summary(self, obj):
        from django.utils import timezone
        license_record = obj.lister.practitioner_licenses.filter(
            status=PractitionerLicense.Status.VERIFIED,
            valid_until__gte=timezone.localdate(),
        ).order_by("-valid_until").first()
        if not license_record:
            return {"status": "not_verified"}
        number = license_record.license_number
        return {
            "status": "verified",
            "license_type": license_record.license_type,
            "number_masked": f"••••{number[-4:]}",
            "checked_at": license_record.source_checked_at,
            "valid_until": license_record.valid_until,
            "source_url": license_record.source_url,
        }

    class Meta:
        model = Listing
        fields = ("id", "charges", "lister_license_summary", "property", "property_title", "lister", "authorization", "offer_type", "headline", "description", "unit_label", "price", "currency", "billing_period", "advance_months", "deposit_amount", "agent_fee_amount", "viewing_fee_amount", "service_charge_amount", "other_fees_amount", "other_fees_description", "costs_disclosed", "estimated_upfront_total", "availability_freshness", "availability_confirmed_at", "available_from", "published_at", "expires_at", "status", "moderated_by", "moderated_at", "moderation_note", "created_at", "updated_at")
        read_only_fields = ("id", "property_title", "lister", "estimated_upfront_total", "availability_confirmed_at", "published_at", "status", "moderated_by", "moderated_at", "moderation_note", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        for field in ("price", "deposit_amount", "agent_fee_amount", "viewing_fee_amount", "service_charge_amount", "other_fees_amount"):
            value = attrs.get(field, getattr(self.instance, field, 0) if self.instance else 0)
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "Amounts cannot be negative."})
        if request is None:
            return attrs
        authorization = attrs.get("authorization", getattr(self.instance, "authorization", None))
        property_obj = attrs.get("property", getattr(self.instance, "property", None))
        if authorization:
            if authorization.property_id != property_obj.pk:
                raise serializers.ValidationError({"authorization": "Authorization must match the listing property."})
            if authorization.lister_id != request.user.pk:
                raise serializers.ValidationError({"authorization": "You are not the lister named in this authorization."})
            if authorization.status not in (ListingAuthorization.Status.REQUESTED, ListingAuthorization.Status.APPROVED):
                raise serializers.ValidationError({"authorization": "This authorization is no longer usable."})
        if self.instance and self.instance.status not in (Listing.Status.DRAFT, Listing.Status.REJECTED):
            raise serializers.ValidationError("Only draft or rejected listings can be edited.")
        return attrs


    def create(self, validated_data):
        return Listing.objects.create(lister=self.context["request"].user, **validated_data)

class ListingModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ("status", "moderation_note")

class ListingAvailabilityConfirmationSerializer(serializers.ModelSerializer):
    confirmed_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ListingAvailabilityConfirmation
        fields = ("id", "listing", "confirmed_by", "is_available", "note", "confirmed_at")
        read_only_fields = ("id", "listing", "confirmed_by", "confirmed_at")
