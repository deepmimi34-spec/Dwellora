from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import Profile
from .models import ProductFeedback
from .views import ProductFeedbackListCreate, ProductFeedbackTriage


class ProductFeedbackTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.member = Profile.objects.create_user(username="feedback_submitter", password="Strong-password-1!", bio="Member")
        self.other = Profile.objects.create_user(username="feedback_other", password="Strong-password-1!", bio="Member")
        self.staff = Profile.objects.create_user(username="feedback_staff", password="Strong-password-1!", bio="Staff", is_staff=True)

    def payload(self):
        return {
            "category": ProductFeedback.Category.USABILITY,
            "title": "The filters are confusing",
            "description": "I cannot tell which filters are currently active.",
            "page_context": "/search",
            "device_context": "Android mobile browser",
            "allow_public_idea": False,
        }

    def test_member_can_submit_feedback_and_is_bound_to_account(self):
        request = self.factory.post("/feedback/", self.payload(), format="json")
        force_authenticate(request, user=self.member)
        response = ProductFeedbackListCreate.as_view()(request)
        self.assertEqual(response.status_code, 201)
        feedback = ProductFeedback.objects.get(pk=response.data["id"])
        self.assertEqual(feedback.profile_id, self.member.pk)
        self.assertEqual(feedback.status, ProductFeedback.Status.RECEIVED)
        self.assertEqual(feedback.severity, ProductFeedback.Severity.NORMAL)

    def test_member_cannot_set_staff_triage_fields_on_submission(self):
        payload = self.payload()
        payload.update({"status": "shipped", "severity": "critical", "internal_note": "Spoofed"})
        request = self.factory.post("/feedback/", payload, format="json")
        force_authenticate(request, user=self.member)
        response = ProductFeedbackListCreate.as_view()(request)
        self.assertEqual(response.status_code, 201)
        feedback = ProductFeedback.objects.get(pk=response.data["id"])
        self.assertEqual(feedback.status, ProductFeedback.Status.RECEIVED)
        self.assertEqual(feedback.severity, ProductFeedback.Severity.NORMAL)
        self.assertEqual(feedback.internal_note, "")

    def test_member_only_sees_own_feedback(self):
        own = ProductFeedback.objects.create(profile=self.member, **self.payload())
        ProductFeedback.objects.create(profile=self.other, **self.payload())
        request = self.factory.get("/feedback/")
        force_authenticate(request, user=self.member)
        response = ProductFeedbackListCreate.as_view()(request)
        self.assertEqual([row["id"] for row in response.data], [own.pk])

    def test_staff_can_triage_and_publish_anonymised_resolution_summary(self):
        feedback = ProductFeedback.objects.create(profile=self.member, **self.payload())
        request = self.factory.patch(f"/feedback/{feedback.pk}/triage/", {
            "status": ProductFeedback.Status.SHIPPED,
            "severity": ProductFeedback.Severity.HIGH,
            "internal_note": "Confirmed issue in current build.",
            "resolution_summary": "The filter indicator was improved.",
        }, format="json")
        force_authenticate(request, user=self.staff)
        response = ProductFeedbackTriage.as_view()(request, pk=feedback.pk)
        self.assertEqual(response.status_code, 200)
        feedback.refresh_from_db()
        self.assertEqual(feedback.status, ProductFeedback.Status.SHIPPED)
        self.assertEqual(feedback.reviewed_by_id, self.staff.pk)
        self.assertIsNotNone(feedback.reviewed_at)

    def test_non_staff_cannot_triage(self):
        feedback = ProductFeedback.objects.create(profile=self.member, **self.payload())
        request = self.factory.patch(f"/feedback/{feedback.pk}/triage/", {"status": "planned"}, format="json")
        force_authenticate(request, user=self.member)
        response = ProductFeedbackTriage.as_view()(request, pk=feedback.pk)
        self.assertEqual(response.status_code, 403)

    def test_status_change_requires_staff_review_metadata(self):
        feedback = ProductFeedback.objects.create(profile=self.member, **self.payload())
        feedback.status = ProductFeedback.Status.PLANNED
        with self.assertRaises(ValidationError):
            feedback.full_clean()
