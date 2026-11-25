from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from property.models import Property, PropertyComment, PropertyContentReport
from property.feedback_views import (
    PropertyContentReportListCreate,
    PropertyContentReportStatusUpdate,
)


class PropertyContentReportTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.member = Profile.objects.create_user(
            username='report_member',
            password='A-strong-password-948!',
            bio='Member',
        )
        self.other = Profile.objects.create_user(
            username='reported_author',
            password='A-strong-password-948!',
            bio='Other',
        )
        self.staff = Profile.objects.create_user(
            username='report_staff',
            password='A-strong-password-948!',
            bio='Staff',
            is_staff=True,
        )
        self.property = Property.objects.create(
            title='Report test apartment',
            property_type='Apartment',
            region='Ashanti',
            city='Kumasi',
        )
        self.comment = PropertyComment.objects.create(
            property=self.property,
            author=self.other,
            body='A public comment to report.',
            moderation_status=PropertyComment.ModerationStatus.PUBLISHED,
        )

    def test_member_can_report_another_members_comment(self):
        request = self.factory.post('/reports/', {
            'comment': self.comment.pk,
            'reason': PropertyContentReport.Reason.MISLEADING,
            'details': 'This comment appears to be misleading.',
        }, format='json')
        force_authenticate(request, user=self.member)

        response = PropertyContentReportListCreate.as_view()(request)

        self.assertEqual(response.status_code, 201)
        report = PropertyContentReport.objects.get(pk=response.data['id'])
        self.assertEqual(report.reporter_id, self.member.pk)
        self.assertEqual(report.status, PropertyContentReport.Status.NEW)

    def test_member_cannot_report_their_own_content(self):
        own_comment = PropertyComment.objects.create(
            property=self.property,
            author=self.member,
            body='My own comment.',
        )
        request = self.factory.post('/reports/', {
            'comment': own_comment.pk,
            'reason': PropertyContentReport.Reason.SPAM,
        }, format='json')
        force_authenticate(request, user=self.member)

        response = PropertyContentReportListCreate.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PropertyContentReport.objects.count(), 0)

    def test_member_cannot_report_the_same_content_twice(self):
        PropertyContentReport.objects.create(
            reporter=self.member,
            comment=self.comment,
            reason=PropertyContentReport.Reason.MISLEADING,
        )
        request = self.factory.post('/reports/', {
            'comment': self.comment.pk,
            'reason': PropertyContentReport.Reason.MISLEADING,
        }, format='json')
        force_authenticate(request, user=self.member)

        response = PropertyContentReportListCreate.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PropertyContentReport.objects.count(), 1)

    def test_member_can_only_see_their_own_reports(self):
        own = PropertyContentReport.objects.create(
            reporter=self.member,
            comment=self.comment,
            reason=PropertyContentReport.Reason.SPAM,
        )
        another_comment = PropertyComment.objects.create(
            property=self.property,
            author=self.member,
            body='Different report target.',
        )
        PropertyContentReport.objects.create(
            reporter=self.other,
            comment=another_comment,
            reason=PropertyContentReport.Reason.OTHER,
        )
        request = self.factory.get('/reports/')
        force_authenticate(request, user=self.member)

        response = PropertyContentReportListCreate.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [own.pk])

    def test_only_staff_can_resolve_a_report(self):
        report = PropertyContentReport.objects.create(
            reporter=self.member,
            comment=self.comment,
            reason=PropertyContentReport.Reason.SPAM,
        )
        member_request = self.factory.patch(
            f'/reports/{report.pk}/status/',
            {'status': PropertyContentReport.Status.DISMISSED},
            format='json',
        )
        force_authenticate(member_request, user=self.member)

        member_response = PropertyContentReportStatusUpdate.as_view()(
            member_request,
            pk=report.pk,
        )

        self.assertEqual(member_response.status_code, 403)

        staff_request = self.factory.patch(
            f'/reports/{report.pk}/status/',
            {
                'status': PropertyContentReport.Status.ACTIONED,
                'resolution_note': 'Comment hidden after review.',
            },
            format='json',
        )
        force_authenticate(staff_request, user=self.staff)

        staff_response = PropertyContentReportStatusUpdate.as_view()(
            staff_request,
            pk=report.pk,
        )

        self.assertEqual(staff_response.status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.reviewed_by_id, self.staff.pk)
        self.assertIsNotNone(report.reviewed_at)
        self.assertEqual(report.resolution_note, 'Comment hidden after review.')
