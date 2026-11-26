import uuid

from accounts.models import RolePermissionBridge
from history.models import BusinessChangeHistory
from notifications.models import Notification
from reviews.models import DisputeResolution, ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class ApproveDisputeTests(EvidenceApiTestCase):
    def escalated(self):
        evidence = self.submitted()
        self.reject(evidence)
        self.escalate(evidence, self.tina)
        case = ReviewRequest.objects.get(kind="DISPUTE")
        return evidence, case

    def test_an_admin_approves_and_the_account_becomes_the_accepted_version(self):
        evidence, case = self.escalated()
        self.sign_in_as_admin(email="admin@example.com")

        response = self.admin_decides(case.pk, "approve")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "APPROVED")
        self.assertEqual(response.data["admin_reason"], "Seen the photos.")
        report = ReviewRequest.objects.get(pk=evidence["id"])
        self.assertEqual(report.status, "APPROVED")
        self.assertIsNotNone(report.target.condition_record.accepted_version)
        self.assertEqual(
            BusinessChangeHistory.objects.get(action="ACCEPT_CONDITION_VERSION").request, case
        )
        resolution = DisputeResolution.objects.get()
        self.assertEqual(resolution.outcome, "ADMIN_APPROVED")
        self.assertEqual(resolution.resolution_request, case)
        self.assertEqual(case.decisions.get().reviewer_side, "ADMIN")

    def test_a_reason_is_required(self):
        _, case = self.escalated()
        self.sign_in_as_admin(email="admin@example.com")

        self.assertEqual(self.admin_decides(case.pk, "approve", reason="  ").status_code, 400)
        self.assertFalse(DisputeResolution.objects.exists())

    def test_a_case_is_decided_once_and_a_retry_with_the_same_key_changes_nothing(self):
        _, case = self.escalated()
        self.sign_in_as_admin(email="admin@example.com")
        key = uuid.uuid4()
        self.admin_decides(case.pk, "approve", key=key)

        self.assertEqual(self.admin_decides(case.pk, "approve", key=key).status_code, 200)
        self.assertEqual(self.admin_decides(case.pk, "reject").status_code, 400)
        self.assertEqual(DisputeResolution.objects.count(), 1)

    def test_a_case_nobody_escalated_is_a_404(self):
        evidence = self.submitted()
        self.reject(evidence)
        case = ReviewRequest.objects.get(kind="DISPUTE")
        self.sign_in_as_admin(email="admin@example.com")

        self.assertEqual(self.admin_decides(case.pk, "approve").status_code, 404)

    def test_the_tenant_and_the_landlord_are_told(self):
        _, case = self.escalated()
        self.sign_in_as_admin(email="admin@example.com")

        self.admin_decides(case.pk, "approve")

        told = Notification.objects.filter(kind="REVIEW_CASE_DECIDED")
        self.assertEqual({n.recipient for n in told}, {self.tina, self.lou})

    def test_an_admin_without_the_permission_is_refused(self):
        _, case = self.escalated()
        RolePermissionBridge.objects.filter(permission__code="reviews.admin_review").delete()
        self.sign_in_as_admin(email="plain@example.com")

        self.assertEqual(self.admin_decides(case.pk, "approve").status_code, 403)

    def test_a_landlord_cannot_decide(self):
        _, case = self.escalated()
        self.as_user(self.lou)

        self.assertEqual(self.admin_decides(case.pk, "approve").status_code, 403)
