from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Property(models.Model):

    PROPERTY_CHOICES = [
        ('Apartment', 'Apartment'),
        ('Hotel', 'Hotel'),
        ('House', 'House'),
        ('Hostel', 'Hostel'),
    ]

    LOCATION_CHOICES = [
        ('Ahafo', 'Ahafo'),
        ('Ashanti', 'Ashanti'),
        ('Bono', 'Bono'),
        ('Bono East', 'Bono East'),
        ('Central', 'Central'),
        ('Eastern', 'Eastern'),
        ('Greater Accra', 'Greater Accra'),
        ('North East', 'North East'),
        ('Northern', 'Northern'),
        ('Oti', 'Oti'),
        ('Savannah', 'Savannah'),
        ('Upper East', 'Upper East'),
        ('Upper West', 'Upper West'),
        ('Volta', 'Volta'),
        ('Western', 'Western'),
        ('Western North', 'Western North'),
    ]

    title = models.CharField(max_length=100)
    property_type = models.CharField(max_length=20, choices=PROPERTY_CHOICES)
    region = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    city = models.CharField(max_length=50, blank=True, help_text='e.g., Kumasi, Accra')
    furnished = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    water_available = models.BooleanField(default=False)
    internet_available = models.BooleanField(default=False)
    kitchen_available = models.BooleanField(default=False)

    class Meta:
        db_table = 'property'
        verbose_name = 'Property'

    def __str__(self):
        return self.title

    def is_property_complete(self):
        """Return whether the required listing identity and region are present.

        City is optional in the current schema, so it is not required here.
        """
        return bool(self.title and self.region)


class PropertyInteraction(models.Model):
    """Records a property-related experience; only staff may mark it verified."""

    class InteractionType(models.TextChoices):
        VIEWING = 'viewing', 'Viewing'
        TENANCY = 'tenancy', 'Tenancy'
        SHORT_STAY = 'short_stay', 'Short stay'
        PURCHASE = 'purchase', 'Purchase'

    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    class VerificationStatus(models.TextChoices):
        UNVERIFIED = 'unverified', 'Unverified'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='interactions',
    )
    profile = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_interactions',
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='verified_property_interactions',
        blank=True,
        null=True,
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_interaction'
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.verification_status == self.VerificationStatus.VERIFIED:
            if self.status != self.Status.COMPLETED:
                raise ValidationError('Only a completed interaction can be verified.')
            if not self.verified_by_id or not self.verified_at:
                raise ValidationError('Verification requires a staff reviewer and timestamp.')
            if not self.verified_by.is_staff:
                raise ValidationError('Only a staff account can verify an interaction.')
        elif self.verified_by_id or self.verified_at:
            raise ValidationError('Unverified interactions cannot have verification metadata.')

    def mark_verified(self, staff_user):
        if not getattr(staff_user, 'is_staff', False):
            raise ValidationError('Only staff can verify an interaction.')
        if self.status != self.Status.COMPLETED:
            raise ValidationError('Complete the interaction before verifying it.')
        self.verification_status = self.VerificationStatus.VERIFIED
        self.verified_by = staff_user
        self.verified_at = timezone.now()
        self.full_clean()
        self.save(update_fields=[
            'verification_status',
            'verified_by',
            'verified_at',
            'updated_at',
        ])

    def is_review_eligible(self):
        return (
            self.status == self.Status.COMPLETED
            and self.verification_status == self.VerificationStatus.VERIFIED
            and self.verified_by_id is not None
            and self.verified_at is not None
        )

    def __str__(self):
        return f'{self.profile.username} · {self.property.title} · {self.interaction_type}'


class PropertyReview(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending moderation'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'

    interaction = models.OneToOneField(
        PropertyInteraction,
        on_delete=models.CASCADE,
        related_name='review',
    )
    headline = models.CharField(max_length=120)
    body = models.TextField(max_length=4000)
    listing_accuracy = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    property_condition = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    communication = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    location_access = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    value_for_money = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    overall_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_review'
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.interaction_id and not self.interaction.is_review_eligible():
            raise ValidationError({
                'interaction': 'A review requires a completed, staff-verified interaction.'
            })

    def __str__(self):
        return f'{self.interaction.property.title} · {self.overall_rating}/5'


class PropertyComment(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending moderation'
        PUBLISHED = 'published', 'Published'
        HIDDEN = 'hidden', 'Hidden'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_comments',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True,
    )
    body = models.TextField(max_length=2000)
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
    )
    is_official = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_comment'
        ordering = ['created_at']

    def clean(self):
        super().clean()
        if self.parent_id and self.property_id != self.parent.property_id:
            raise ValidationError({
                'parent': 'A reply must belong to the same property as its parent comment.'
            })
        if self.is_official and not self.author.is_staff:
            raise ValidationError('Only staff responses can be marked official.')

    def __str__(self):
        return f'{self.property.title} · {self.body[:60]}'


class PropertyContentReport(models.Model):
    class Reason(models.TextChoices):
        SPAM = 'spam', 'Spam or advertising'
        HARASSMENT = 'harassment', 'Harassment or abuse'
        PRIVATE_INFORMATION = 'private_information', 'Private information'
        MISLEADING = 'misleading', 'Misleading or fabricated content'
        CONFLICT_OF_INTEREST = 'conflict_of_interest', 'Conflict of interest'
        OTHER = 'other', 'Other concern'

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        UNDER_REVIEW = 'under_review', 'Under review'
        ACTIONED = 'actioned', 'Action taken'
        DISMISSED = 'dismissed', 'Dismissed'

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_content_reports',
    )
    review = models.ForeignKey(
        PropertyReview,
        on_delete=models.CASCADE,
        related_name='reports',
        blank=True,
        null=True,
    )
    comment = models.ForeignKey(
        PropertyComment,
        on_delete=models.CASCADE,
        related_name='reports',
        blank=True,
        null=True,
    )
    reason = models.CharField(max_length=30, choices=Reason.choices)
    details = models.TextField(max_length=2000, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reviewed_property_reports',
        blank=True,
        null=True,
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    resolution_note = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_content_report'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['reporter', 'review'],
                condition=models.Q(review__isnull=False),
                name='unique_reporter_property_review',
            ),
            models.UniqueConstraint(
                fields=['reporter', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_reporter_property_comment',
            ),
        ]

    def clean(self):
        super().clean()
        if bool(self.review_id) == bool(self.comment_id):
            raise ValidationError('A report must target exactly one review or comment.')
        if self.review_id and self.review.interaction.profile_id == self.reporter_id:
            raise ValidationError('You cannot report your own property review.')
        if self.comment_id and self.comment.author_id == self.reporter_id:
            raise ValidationError('You cannot report your own property comment.')
        if self.status != self.Status.NEW:
            if not self.reviewed_by_id or not self.reviewed_by.is_staff or not self.reviewed_at:
                raise ValidationError('Report status changes require staff review metadata.')

    def __str__(self):
        target = f'Review {self.review_id}' if self.review_id else f'Comment {self.comment_id}'
        return f'{target} reported by {self.reporter.username}'


# Ownership and marketplace offer models are separated from the physical property.
from .listing_models import PropertyOwnership, ListingAuthorization, Listing
