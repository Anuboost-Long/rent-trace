from reviews.models import DisputeResolution, ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class RejectDisputeTests(EvidenceApiTestCase):
    def test_an_admin_rejects_and_the_record_is_left_as_it_was(self):
        evidence = self.submitted()
        self.expire(evidence)
        self.escalate(evidence, self.tina)
        case = ReviewRequest.objects.get(kind="DISPUTE")
        self.sign_in_as_admin(email="admin@example.com")

        response = self.admin_decides(case.pk, "reject", reason="No proof.")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "REJECTED")
        report = ReviewRequest.objects.get(pk=evidence["id"])
        self.assertEqual(report.status, "REJECTED")
        self.assertIsNone(report.target.condition_record.accepted_version)
        resolution = DisputeResolution.objects.get()
        self.assertEqual((resolution.outcome, resolution.reason), ("ADMIN_REJECTED", "No proof."))
        self.assertIsNone(resolution.result_condition_version)
