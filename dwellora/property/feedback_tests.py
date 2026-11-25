from datetime import date
from types import SimpleNamespace

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from .models import (
    Property,
    PropertyComment,
    PropertyInteraction,
    PropertyReview,
)
from .feedback_serializers import PropertyReviewSerializer
from .feedback_views import (
    PropertyCommentCreate,
    PropertyCommentList,
    PropertyCommentModerationUpdate,
    PropertyReviewCreate,
    PropertyReviewList,
    PropertyReviewModerationUpdate,
)


class PropertyFeedbackFixture(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.member = Profile.objects.create_user(
            username='feedback_member',
            password='A-strong-password-948!',
            bio='Member',
        )
        self.other_member = Profile.objects.create_user(
            username='feedback_other',
            password='A-strong-password-948!',
            bio='Other member',
        )
        self.staff = Profile.objects.create_user(
            username='feedback_staff',
            password='A-strong-password-948!',
            bio='Staff',
            is_staff=True,
        )
        self.property_record = Property.objects.create(
            title='Garden City Apartment',
            property_type='Apartment',
            region='Ashanti',
            city='Kumasi',
        )
        self.other_property = Property.objects.create(
            title='Airport Residential House',
            property_type='House',
            region='Greater Accra',
            city='Accra',
        )

    def make_completed_interaction(self, profile=None, property_record=None):
        interaction = PropertyInteraction.objects.create(
            property=property_record or self.property_record,
            profile=profile or self.member,
            interaction_type=PropertyInteraction.InteractionType.TENANCY,
            status=PropertyInteraction.Status.COMPLETED,
        )
        return interaction

    def review_payload(self, interaction):
        return {
            'interaction': interaction.pk,
            'headline': 'Accurate listing and good communication',
            'body': 'The property matched the listing and communication was clear.',
            'listing_accuracy': 5,
            'property_condition': 4,
            'communication': 5,
            'location_access': 4,
            'value_for_money': 4,
            'overall_rating': 5,
        }


class PropertyInteractionVerificationTests(PropertyFeedbackFixture):
    def test_only_staff_can_verify_interaction(self):
        interaction = self.make_completed_interaction()

        with self.assertRaises(DjangoValidationError):
            interaction.mark_verified(self.member)

        interaction.refresh_from_db()
        self.assertEqual(
            interaction.verification_status,
            PropertyInteraction.VerificationStatus.UNVERIFIED,
        )

    def test_only_completed_interactions_can_be_verified(self):
        interaction = PropertyInteraction.objects.create(
            property=self.property_record,
            profile=self.member,
            interaction_type=PropertyInteraction.InteractionType.VIEWING,
            status=PropertyInteraction.Status.REQUESTED,
        )

        with self.assertRaises(DjangoValidationError):
            interaction.mark_verified(self.staff)

    def test_staff_verification_makes_completed_interaction_review_eligible(self):
        interaction = self.make_completed_interaction()

        interaction.mark_verified(self.staff)
        interaction.refresh_from_db()

        self.assertTrue(interaction.is_review_eligible())
        self.assertEqual(interaction.verified_by_id, self.staff.pk)
        self.assertIsNotNone(interaction.verified_at)


class PropertyReviewEligibilityTests(PropertyFeedbackFixture):
    def test_unverified_interaction_cannot_be_reviewed(self):
        interaction = self.make_completed_interaction()
        request = SimpleNamespace(user=self.member)
        serializer = PropertyReviewSerializer(
            data=self.review_payload(interaction),
            context={'request': request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('interaction', serializer.errors)

    def test_member_cannot_review_another_users_interaction(self):
        interaction = self.make_completed_interaction()
        interaction.mark_verified(self.staff)
        request = SimpleNamespace(user=self.other_member)
        serializer = PropertyReviewSerializer(
            data=self.review_payload(interaction),
            context={'request': request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('interaction', serializer.errors)

    def test_one_review_can_be_created_for_a_verified_interaction(self):
        interaction = self.make_completed_interaction()
        interaction.mark_verified(self.staff)
        request = SimpleNamespace(user=self.member)
        serializer = PropertyReviewSerializer(
            data=self.review_payload(interaction),
            context={'request': request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        review = serializer.save()

        self.assertEqual(review.interaction_id, interaction.pk)
        self.assertEqual(review.moderation_status, PropertyReview.ModerationStatus.PENDING)

    def test_interaction_cannot_receive_a_second_review(self):
        interaction = self.make_completed_interaction()
        interaction.mark_verified(self.staff)
        first = PropertyReviewSerializer(
            data=self.review_payload(interaction),
            context={'request': SimpleNamespace(user=self.member)},
        )
        self.assertTrue(first.is_valid(), first.errors)
        first.save()

        duplicate = PropertyReviewSerializer(
            data=self.review_payload(interaction),
            context={'request': SimpleNamespace(user=self.member)},
        )

        self.assertFalse(duplicate.is_valid())
        self.assertIn('interaction', duplicate.errors)

    def test_review_rating_values_must_be_between_one_and_five(self):
        interaction = self.make_completed_interaction()
        interaction.mark_verified(self.staff)
        payload = self.review_payload(interaction)
        payload['overall_rating'] = 6
        serializer = PropertyReviewSerializer(
            data=payload,
            context={'request': SimpleNamespace(user=self.member)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('overall_rating', serializer.errors)


class PropertyCommentModerationTests(PropertyFeedbackFixture):
    def test_member_comment_is_held_for_moderation(self):
        request = self.factory.post(
            '/api/property/feedback/comments/',
            {'body': 'Is water available every day?'},
            format='json',
        )
        force_authenticate(request, user=self.member)

        response = PropertyCommentCreate.as_view()(
            request,
            property_pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 201)
        comment = PropertyComment.objects.get(pk=response.data['id'])
        self.assertEqual(comment.author_id, self.member.pk)
        self.assertEqual(
            comment.moderation_status,
            PropertyComment.ModerationStatus.PENDING,
        )
        self.assertFalse(comment.is_official)

    def test_staff_comment_is_published_as_an_official_response(self):
        request = self.factory.post(
            '/api/property/feedback/comments/',
            {'body': 'Dwellora has confirmed this detail with the listing manager.'},
            format='json',
        )
        force_authenticate(request, user=self.staff)

        response = PropertyCommentCreate.as_view()(
            request,
            property_pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 201)
        comment = PropertyComment.objects.get(pk=response.data['id'])
        self.assertEqual(
            comment.moderation_status,
            PropertyComment.ModerationStatus.PUBLISHED,
        )
        self.assertTrue(comment.is_official)

    def test_public_comment_list_hides_pending_comments(self):
        PropertyComment.objects.create(
            property=self.property_record,
            author=self.member,
            body='Waiting for review',
            moderation_status=PropertyComment.ModerationStatus.PENDING,
        )
        PropertyComment.objects.create(
            property=self.property_record,
            author=self.staff,
            body='Official answer',
            moderation_status=PropertyComment.ModerationStatus.PUBLISHED,
            is_official=True,
        )
        request = self.factory.get('/api/property/feedback/comments/')

        response = PropertyCommentList.as_view()(
            request,
            property_pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['body'], 'Official answer')

    def test_author_can_see_own_pending_comment(self):
        pending = PropertyComment.objects.create(
            property=self.property_record,
            author=self.member,
            body='My question is awaiting moderation.',
        )
        request = self.factory.get('/api/property/feedback/comments/')
        force_authenticate(request, user=self.member)

        response = PropertyCommentList.as_view()(
            request,
            property_pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [pending.pk])

    def test_reply_cannot_be_attached_to_a_different_property(self):
        parent = PropertyComment.objects.create(
            property=self.other_property,
            author=self.other_member,
            body='Parent comment on another property.',
        )
        request = self.factory.post(
            '/api/property/feedback/comments/',
            {
                'body': 'A reply attached to the wrong property.',
                'parent': parent.pk,
            },
            format='json',
        )
        force_authenticate(request, user=self.member)

        response = PropertyCommentCreate.as_view()(
            request,
            property_pk=self.property_record.pk,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PropertyComment.objects.count(), 1)

    def test_staff_can_publish_a_pending_comment(self):
        comment = PropertyComment.objects.create(
            property=self.property_record,
            author=self.member,
            body='Awaiting moderation.',
        )
        request = self.factory.patch(
            f'/api/property/feedback/comments/{comment.pk}/moderation/',
            {'moderation_status': PropertyComment.ModerationStatus.PUBLISHED},
            format='json',
        )
        force_authenticate(request, user=self.staff)

        response = PropertyCommentModerationUpdate.as_view()(
            request,
            pk=comment.pk,
        )

        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(
            comment.moderation_status,
            PropertyComment.ModerationStatus.PUBLISHED,
        )


class PropertyReviewModerationTests(PropertyFeedbackFixture):
    def test_public_review_list_only_returns_published_reviews(self):
        interaction = self.make_completed_interaction()
        interaction.mark_verified(self.staff)
        serializer = PropertyReviewSerializer(
            data=self.review_payload(interaction),
            context={'request': SimpleNamespace(user=self.member)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        review = serializer.save()

        request = self.factory.get('/api/property/feedback/reviews/')
        hidden_response = PropertyReviewList.as_view()(
            request,
            property_pk=self.property_record.pk,
        )
        self.assertEqual(len(hidden_response.data), 0)

        moderation_request = self.factory.patch(
            f'/api/property/feedback/reviews/{review.pk}/moderation/',
            {'moderation_status': PropertyReview.ModerationStatus.PUBLISHED},
            format='json',
        )
        force_authenticate(moderation_request, user=self.staff)
        moderation_response = PropertyReviewModerationUpdate.as_view()(
            moderation_request,
            pk=review.pk,
        )
        self.assertEqual(moderation_response.status_code, 200)

        public_response = PropertyReviewList.as_view()(
            request,
            property_pk=self.property_record.pk,
        )
        self.assertEqual(len(public_response.data), 1)
        self.assertEqual(public_response.data[0]['overall_rating'], 5)
