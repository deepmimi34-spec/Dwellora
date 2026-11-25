from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from property.models import Property, PropertyInteraction
from property.feedback_views import (
    PropertyInteractionListCreate,
    PropertyInteractionStatusUpdate,
    PropertyInteractionVerify,
)


class PropertyInteractionWorkflowTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.member = Profile.objects.create_user(
            username='interaction_member',
            password='A-strong-password-948!',
            bio='Member',
        )
        self.other = Profile.objects.create_user(
            username='interaction_other',
            password='A-strong-password-948!',
            bio='Other',
        )
        self.staff = Profile.objects.create_user(
            username='interaction_staff',
            password='A-strong-password-948!',
            bio='Staff',
            is_staff=True,
        )
        self.property = Property.objects.create(
            title='Kumasi Apartment',
            property_type='Apartment',
            region='Ashanti',
            city='Kumasi',
        )

    def create_interaction(self, profile):
        return PropertyInteraction.objects.create(
            property=self.property,
            profile=profile,
            interaction_type=PropertyInteraction.InteractionType.VIEWING,
        )

    def test_member_can_request_viewing_and_is_assigned_as_owner(self):
        request = self.factory.post('/interactions/', {
            'property': self.property.pk,
            'interaction_type': 'viewing',
        }, format='json')
        force_authenticate(request, user=self.member)

        response = PropertyInteractionListCreate.as_view()(request)

        self.assertEqual(response.status_code, 201)
        interaction = PropertyInteraction.objects.get(pk=response.data['id'])
        self.assertEqual(interaction.profile_id, self.member.pk)
        self.assertEqual(interaction.status, PropertyInteraction.Status.REQUESTED)
        self.assertEqual(
            interaction.verification_status,
            PropertyInteraction.VerificationStatus.UNVERIFIED,
        )

    def test_member_cannot_assign_interaction_to_another_profile(self):
        request = self.factory.post('/interactions/', {
            'property': self.property.pk,
            'profile': self.other.pk,
            'interaction_type': 'viewing',
        }, format='json')
        force_authenticate(request, user=self.member)

        response = PropertyInteractionListCreate.as_view()(request)

        self.assertEqual(response.status_code, 201)
        interaction = PropertyInteraction.objects.get(pk=response.data['id'])
        self.assertEqual(interaction.profile_id, self.member.pk)

    def test_member_sees_only_their_own_interactions(self):
        own = self.create_interaction(self.member)
        self.create_interaction(self.other)
        request = self.factory.get('/interactions/')
        force_authenticate(request, user=self.member)

        response = PropertyInteractionListCreate.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [own.pk])

    def test_member_cannot_mark_interaction_completed(self):
        interaction = self.create_interaction(self.member)
        request = self.factory.patch(
            f'/interactions/{interaction.pk}/status/',
            {'status': 'completed'},
            format='json',
        )
        force_authenticate(request, user=self.member)

        response = PropertyInteractionStatusUpdate.as_view()(
            request,
            pk=interaction.pk,
        )

        self.assertEqual(response.status_code, 403)
        interaction.refresh_from_db()
        self.assertEqual(interaction.status, PropertyInteraction.Status.REQUESTED)

    def test_staff_can_complete_and_verify_interaction(self):
        interaction = self.create_interaction(self.member)
        status_request = self.factory.patch(
            f'/interactions/{interaction.pk}/status/',
            {'status': 'completed'},
            format='json',
        )
        force_authenticate(status_request, user=self.staff)

        status_response = PropertyInteractionStatusUpdate.as_view()(
            status_request,
            pk=interaction.pk,
        )
        self.assertEqual(status_response.status_code, 200)

        verify_request = self.factory.post(
            f'/interactions/{interaction.pk}/verify/'
        )
        force_authenticate(verify_request, user=self.staff)
        verify_response = PropertyInteractionVerify.as_view()(
            verify_request,
            pk=interaction.pk,
        )

        self.assertEqual(verify_response.status_code, 200)
        interaction.refresh_from_db()
        self.assertTrue(interaction.is_review_eligible())
        self.assertEqual(interaction.verified_by_id, self.staff.pk)
