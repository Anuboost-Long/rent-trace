from notifications.models import Notification
from reviews.models import ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class EscalateEvidenceTests(EvidenceApiTestCase):
    def rejected(self):
        evidence = self.submitted()
        self.assertEqual(self.reject(evidence).status_code, 200)
        return evidence

    def case_of(self, evidence):
        return ReviewRequest.objects.get(kind="DISPUTE", parent_request_id=evidence["id"])

    def test_the_tenant_escalates_a_rejected_report_to_an_admin(self):
        evidence = self.rejected()
        self.sign_in_as_admin(email="admin@example.com")

        response = self.escalate(evidence, self.tina, reason="  The landlord never looked.  ")

        self.assertEqual(response.status_code, 200, response.data)
        case = self.case_of(evidence)
        self.assertEqual(case.review_route, "ADMIN")
        self.assertEqual(case.status, "PENDING_REVIEW")
        row = case.status_history.get(action="ESCALATE")
        self.assertEqual(row.reason, "The landlord never looked.")
        self.assertEqual(row.actor, self.tina)
        self.assertIsNotNone(response.data["escalated_at"])

    def test_the_landlord_can_escalate_a_rejection_too(self):
        evidence = self.rejected()

        response = self.escalate(evidence, self.lou)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.case_of(evidence).review_route, "ADMIN")

    def test_the_tenant_escalates_an_expired_report_and_a_case_is_created(self):
        evidence = self.submitted()
        self.expire(evidence)

        response = self.escalate(evidence, self.tina)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "DISPUTED")
        case = self.case_of(evidence)
        self.assertEqual((case.review_route, case.requester_side), ("ADMIN", "TENANT"))
        self.assertEqual(case.dispute.details, "Please decide.")

    def test_it_needs_a_reason(self):
        evidence = self.rejected()

        self.assertEqual(self.escalate(evidence, self.tina, reason="   ").status_code, 400)
        self.assertEqual(self.escalate(evidence, self.tina, reason="").status_code, 400)
        self.assertEqual(self.case_of(evidence).review_route, "OPPOSITE_SIDE")

    def test_a_waiting_approved_or_withdrawn_report_cannot_be_escalated(self):
        waiting = self.submitted()
        self.assertEqual(self.escalate(waiting, self.tina).status_code, 400)
        approved = self.submitted()
        self.approve(approved)
        self.assertEqual(self.escalate(approved, self.tina).status_code, 400)
        withdrawn = self.submitted()
        self.as_user(self.tina)
        self.post(f"{self.tenant_url}{withdrawn['id']}/cancel/")
        self.assertEqual(self.escalate(withdrawn, self.tina).status_code, 400)

    def test_escalating_twice_is_refused_and_makes_one_case(self):
        evidence = self.rejected()
        self.escalate(evidence, self.tina)

        self.assertEqual(self.escalate(evidence, self.lou).status_code, 400)
        self.assertEqual(ReviewRequest.objects.filter(kind="DISPUTE").count(), 1)

    def test_escalating_an_expired_report_twice_makes_one_case(self):
        evidence = self.submitted()
        self.expire(evidence)
        self.escalate(evidence, self.tina)

        self.assertEqual(self.escalate(evidence, self.tina).status_code, 400)
        self.assertEqual(ReviewRequest.objects.filter(kind="DISPUTE").count(), 1)

    def test_a_stranger_gets_a_404(self):
        evidence = self.rejected()
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(self.escalate(evidence, self.sam).status_code, 404)
        self.assertEqual(self.escalate(evidence, self.mia).status_code, 404)

    def test_admins_who_can_decide_are_told_with_the_reason(self):
        evidence = self.rejected()
        admin = self.sign_in_as_admin(email="admin@example.com")

        self.escalate(evidence, self.tina, reason="Landlord is unreachable.")

        sent = Notification.objects.get(recipient=admin, kind="REVIEW_CASE_ESCALATED")
        self.assertEqual(sent.subject_id, self.case_of(evidence).pk)
        self.assertIn("Landlord is unreachable.", sent.body)
