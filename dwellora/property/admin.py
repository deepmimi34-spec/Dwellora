from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .listing_models import PropertyOwnership, ListingAuthorization, Listing, ListingAvailabilityConfirmation, ListingCharge


@admin.register(PropertyOwnership)
class PropertyOwnershipAdmin(admin.ModelAdmin):
    list_display = ("property", "claimant", "ownership_type", "status", "submitted_at", "reviewed_by", "reviewed_at")
    list_filter = ("status", "ownership_type", "submitted_at")
    search_fields = ("property__title", "claimant__username", "claimant__email", "evidence_type")
    readonly_fields = ("status", "submitted_at", "reviewed_by", "reviewed_at", "review_note")
    actions = ("verify_claims", "reject_claims", "revoke_claims")

    @admin.action(description="Verify selected ownership claims")
    def verify_claims(self, request, queryset):
        count = 0
        for claim in queryset:
            try:
                claim.review(request.user, PropertyOwnership.Status.VERIFIED, "Reviewed in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{claim}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Verified {count} ownership claim(s).")

    @admin.action(description="Reject selected ownership claims")
    def reject_claims(self, request, queryset):
        count = 0
        for claim in queryset:
            try:
                claim.review(request.user, PropertyOwnership.Status.REJECTED, "Rejected in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{claim}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Rejected {count} ownership claim(s).")

    @admin.action(description="Revoke selected ownership claims")
    def revoke_claims(self, request, queryset):
        count = 0
        for claim in queryset:
            try:
                claim.review(request.user, PropertyOwnership.Status.REVOKED, "Revoked in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{claim}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Revoked {count} ownership claim(s).")


@admin.register(ListingAuthorization)
class ListingAuthorizationAdmin(admin.ModelAdmin):
    list_display = ("property", "ownership", "lister", "authority_type", "status", "valid_from", "valid_until", "reviewed_by")
    list_filter = ("status", "authority_type", "valid_until")
    search_fields = ("property__title", "lister__username", "ownership__claimant__username")
    readonly_fields = ("status", "reviewed_by", "reviewed_at", "review_note")
    actions = ("approve_authorizations", "reject_authorizations", "revoke_authorizations")

    @admin.action(description="Approve selected listing authorizations")
    def approve_authorizations(self, request, queryset):
        count = 0
        for authorization in queryset:
            try:
                authorization.review(request.user, ListingAuthorization.Status.APPROVED, "Approved in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{authorization}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Approved {count} authorization(s).")

    @admin.action(description="Reject selected listing authorizations")
    def reject_authorizations(self, request, queryset):
        count = 0
        for authorization in queryset:
            try:
                authorization.review(request.user, ListingAuthorization.Status.REJECTED, "Rejected in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{authorization}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Rejected {count} authorization(s).")

    @admin.action(description="Revoke selected listing authorizations")
    def revoke_authorizations(self, request, queryset):
        count = 0
        for authorization in queryset:
            try:
                authorization.review(request.user, ListingAuthorization.Status.REVOKED, "Revoked in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{authorization}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Revoked {count} authorization(s).")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("headline", "property", "lister", "offer_type", "price", "currency", "status", "availability_confirmed_at", "created_at")
    list_filter = ("status", "offer_type", "currency", "billing_period", "created_at")
    search_fields = ("headline", "property__title", "lister__username", "lister__email")
    readonly_fields = ("status", "created_at", "updated_at", "published_at", "moderated_by", "moderated_at", "availability_confirmed_at", "moderation_note")
    actions = ("publish_submitted", "reject_submitted", "remove_listings", "pause_listings")

    @admin.action(description="Publish selected submitted listings")
    def publish_submitted(self, request, queryset):
        count = 0
        for listing in queryset:
            try:
                listing.moderate(request.user, Listing.Status.PUBLISHED, "Published in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{listing}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Published {count} listing(s).")

    @admin.action(description="Reject selected submitted listings")
    def reject_submitted(self, request, queryset):
        count = 0
        for listing in queryset:
            try:
                listing.moderate(request.user, Listing.Status.REJECTED, "Rejected in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{listing}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Rejected {count} listing(s).")

    @admin.action(description="Remove selected listings")
    def remove_listings(self, request, queryset):
        count = 0
        for listing in queryset:
            try:
                listing.moderate(request.user, Listing.Status.REMOVED, "Removed in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{listing}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Removed {count} listing(s).")

    @admin.action(description="Pause selected listings")
    def pause_listings(self, request, queryset):
        count = 0
        for listing in queryset:
            try:
                listing.moderate(request.user, Listing.Status.PAUSED, "Paused in Django admin.")
                count += 1
            except ValidationError as exc:
                self.message_user(request, f"{listing}: {exc}", level=messages.ERROR)
        self.message_user(request, f"Paused {count} listing(s).")


@admin.register(ListingAvailabilityConfirmation)
class ListingAvailabilityConfirmationAdmin(admin.ModelAdmin):
    list_display = ("listing", "confirmed_by", "is_available", "confirmed_at")
    list_filter = ("is_available", "confirmed_at")
    search_fields = ("listing__headline", "confirmed_by__username")
    readonly_fields = ("listing", "confirmed_by", "is_available", "note", "confirmed_at")

@admin.register(ListingCharge)
class ListingChargeAdmin(admin.ModelAdmin):
    list_display = ("listing", "charge_type", "amount", "currency", "payer", "frequency", "is_required")
    list_filter = ("charge_type", "payer", "frequency", "is_required", "currency")
    search_fields = ("listing__headline", "listing__property__title", "description")
    readonly_fields = ("created_by", "created_at", "updated_at")
