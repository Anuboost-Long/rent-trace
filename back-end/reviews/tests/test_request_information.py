import uuid

from notifications.models import Notification
from reviews.models import ReviewDecision, ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class RequestInformationTests(EvidenceApiTestCase):
    def test_the_landlord_asks_and_the_report_waits_for_the_tenant(self):
        evidence = self.submitted()

        response = self.ask(evidence)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "NEEDS_INFORMATION")
        self.assertEqual(response.data["information_request"], "Which wall, and when?")
        decision = ReviewDecision.objects.get()
        self.assertEqual(
            (decision.decision, decision.reviewer_side), ("REQUEST_INFORMATION", "LANDLORD")
        )
        history = ReviewRequest.objects.get().status_history.order_by("sequence_no").last()
        self.assertEqual(
            (history.action, history.from_status), ("REQUEST_INFORMATION", "PENDING_REVIEW")
        )

    def test_the_tenant_is_told_with_the_question(self):
        evidence = self.submitted()

        self.ask(evidence, reason="Which wall?")

        sent = Notification.objects.get(
            recipient=self.tina, kind="CONDITION_EVIDENCE_INFO_REQUESTED"
        )
        self.assertIn("Which wall?", sent.body)
        self.assertEqual(sent.subject_id, self.tenancy["id"])

    def test_a_reason_is_required(self):
        evidence = self.submitted()

        self.assertEqual(self.ask(evidence, reason="  ").status_code, 400)
        self.as_user(self.tina)
        self.assertEqual(self.client.get(self.tenant_url).data[0]["status"], "PENDING_REVIEW")

    def test_nobody_can_approve_reject_or_escalate_while_it_waits_for_the_tenant(self):
        evidence = self.submitted()
        self.ask(evidence)

        self.assertEqual(self.approve(evidence).status_code, 400)
        self.assertEqual(self.reject(evidence).status_code, 400)
        self.assertEqual(self.escalate(evidence, self.tina).status_code, 400)
        self.assertEqual(self.ask(evidence).status_code, 400)

    def test_retrying_with_the_same_key_changes_nothing(self):
        evidence = self.submitted()
        key = uuid.uuid4()
        self.ask(evidence, key=key)

        self.assertEqual(self.ask(evidence, key=key).status_code, 200)
        self.assertEqual(ReviewDecision.objects.count(), 1)

    def test_an_expired_report_cannot_be_asked_about(self):
        evidence = self.submitted()
        self.expire(evidence)

        self.assertEqual(self.ask(evidence).status_code, 400)

    def test_the_tenant_cannot_ask_and_another_landlord_gets_a_404(self):
        evidence = self.submitted()

        self.assertEqual(self.ask(evidence, user=self.tina).status_code, 403)
        self.assertEqual(self.ask(evidence, user=self.mia).status_code, 404)

    def test_the_tenant_can_withdraw_it_while_it_waits(self):
        evidence = self.submitted()
        self.ask(evidence)
        self.as_user(self.tina)

        cancelled = self.post(f"{self.tenant_url}{evidence['id']}/cancel/")

        self.assertEqual(cancelled.data["status"], "CANCELLED")
        self.assertEqual(
            ReviewRequest.objects.get().status_history.order_by("sequence_no").last().from_status,
            "NEEDS_INFORMATION",
        )
