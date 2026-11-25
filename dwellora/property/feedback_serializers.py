from rest_framework import serializers

from .models import (
    Property,
    PropertyComment,
    PropertyInteraction,
    PropertyReview,
)


class PropertyReviewSerializer(serializers.ModelSerializer):
    interaction = serializers.PrimaryKeyRelatedField(
        queryset=PropertyInteraction.objects.all(),
        write_only=True,
    )
    property_id = serializers.IntegerField(
        source='interaction.property_id',
        read_only=True,
    )
    reviewer_username = serializers.CharField(
        source='interaction.profile.username',
        read_only=True,
    )

    class Meta:
        model = PropertyReview
        fields = (
            'id',
            'interaction',
            'property_id',
            'reviewer_username',
            'headline',
            'body',
            'listing_accuracy',
            'property_condition',
            'communication',
            'location_access',
            'value_for_money',
            'overall_rating',
            'moderation_status',
            'created_at',
        )
        read_only_fields = (
            'id',
            'property_id',
            'reviewer_username',
            'moderation_status',
            'created_at',
        )

    def validate_interaction(self, interaction):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Sign in to submit a review.')
        if interaction.profile_id != request.user.pk:
            raise serializers.ValidationError(
                'You can only review your own verified property interaction.'
            )
        if not interaction.is_review_eligible():
            raise serializers.ValidationError(
                'Reviews require a completed interaction verified by Dwellora staff.'
            )
        if PropertyReview.objects.filter(interaction=interaction).exists():
            raise serializers.ValidationError(
                'A review has already been submitted for this interaction.'
            )
        return interaction

    def create(self, validated_data):
        review = PropertyReview(**validated_data)
        review.full_clean()
        review.save()
        return review


class PropertyCommentSerializer(serializers.ModelSerializer):
    property_id = serializers.IntegerField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=PropertyComment.objects.all(),
        required=False,
        allow_null=True,
    )
    moderation_status = serializers.CharField(read_only=True)
    is_official = serializers.BooleanField(read_only=True)

    class Meta:
        model = PropertyComment
        fields = (
            'id',
            'property_id',
            'author_username',
            'parent',
            'body',
            'moderation_status',
            'is_official',
            'created_at',
        )
        read_only_fields = (
            'id',
            'property_id',
            'author_username',
            'moderation_status',
            'is_official',
            'created_at',
        )

    def validate_parent(self, parent):
        if parent:
            view = self.context.get('view')
            property_pk = view.kwargs.get('property_pk') if view else None
            if property_pk and parent.property_id != int(property_pk):
                raise serializers.ValidationError(
                    'A reply must belong to the same property as its parent comment.'
                )
        return parent

    def create(self, validated_data):
        request = self.context['request']
        view = self.context['view']
        property_record = Property.objects.get(pk=view.kwargs['property_pk'])
        is_official = bool(request.user.is_staff)
        comment = PropertyComment(
            property=property_record,
            author=request.user,
            is_official=is_official,
            moderation_status=(
                PropertyComment.ModerationStatus.PUBLISHED
                if is_official
                else PropertyComment.ModerationStatus.PENDING
            ),
            **validated_data,
        )
        comment.full_clean()
        comment.save()
        return comment


class PropertyReviewModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyReview
        fields = ('moderation_status',)


class PropertyCommentModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyComment
        fields = ('moderation_status',)


class PropertyInteractionSerializer(serializers.ModelSerializer):
    profile_username = serializers.CharField(source='profile.username', read_only=True)
    status = serializers.CharField(read_only=True)
    verification_status = serializers.CharField(read_only=True)
    verified_by = serializers.PrimaryKeyRelatedField(read_only=True)
    verified_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PropertyInteraction
        fields = (
            'id', 'property', 'profile_username', 'interaction_type', 'status',
            'verification_status', 'verified_by', 'verified_at',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'profile_username', 'status', 'verification_status',
            'verified_by', 'verified_at', 'created_at', 'updated_at',
        )


class PropertyInteractionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInteraction
        fields = ('status',)

    def update(self, instance, validated_data):
        from django.core.exceptions import ValidationError as DjangoValidationError

        new_status = validated_data.get('status', instance.status)
        if (
            instance.verification_status == PropertyInteraction.VerificationStatus.VERIFIED
            and new_status != PropertyInteraction.Status.COMPLETED
        ):
            raise serializers.ValidationError(
                {'status': 'A verified interaction cannot be changed.'}
            )
        instance.status = new_status
        try:
            instance.full_clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error
        instance.save(update_fields=['status', 'updated_at'])
        return instance


class PropertyContentReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    status = serializers.CharField(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True)
    resolution_note = serializers.CharField(read_only=True)

    class Meta:
        model = PropertyContentReport
        fields = (
            'id', 'review', 'comment', 'reason', 'details',
            'reporter_username', 'status', 'reviewed_by',
            'reviewed_at', 'resolution_note', 'created_at',
        )
        read_only_fields = (
            'id', 'reporter_username', 'status', 'reviewed_by',
            'reviewed_at', 'resolution_note', 'created_at',
        )

    def validate(self, attrs):
        review = attrs.get('review')
        comment = attrs.get('comment')
        if bool(review) == bool(comment):
            raise serializers.ValidationError(
                'Choose exactly one review or comment to report.'
            )
        request = self.context.get('request')
        if review and review.interaction.profile_id == request.user.pk:
            raise serializers.ValidationError('You cannot report your own review.')
        if comment and comment.author_id == request.user.pk:
            raise serializers.ValidationError('You cannot report your own comment.')
        if PropertyContentReport.objects.filter(
            reporter=request.user, review=review, comment=comment
        ).exists():
            raise serializers.ValidationError(
                'You have already reported this content.'
            )
        return attrs

    def create(self, validated_data):
        from django.core.exceptions import ValidationError as DjangoValidationError

        report = PropertyContentReport(
            reporter=self.context['request'].user,
            **validated_data,
        )
        try:
            report.full_clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error
        report.save()
        return report


class PropertyContentReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyContentReport
        fields = ('status', 'resolution_note')
