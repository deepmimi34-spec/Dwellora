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
        if not interaction.is_review_eligible:
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
