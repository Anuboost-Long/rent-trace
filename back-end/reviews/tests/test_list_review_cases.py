from reviews.models import ReviewRequest
from reviews.tests.base import ADMIN_URL, EvidenceApiTestCase


class ListReviewCasesTests(EvidenceApiTestCase):
    def test_the_queue_holds_only_escalated_cases_waiting_for_a_decision(self):
        rejected_only = self.submitted()
        self.reject(rejected_only)
        escalated = self.submitted()
        self.reject(escalated)
        self.escalate(escalated, self.tina, reason="Landlord is unreachable.")
        self.sign_in_as_admin(email="admin@example.com")

        listed = self.client.get(ADMIN_URL)

        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["count"], 1)
        row = listed.data["results"][0]
        self.assertEqual(row["report_id"], escalated["id"])
        self.assertEqual(row["escalation_reason"], "Landlord is unreachable.")
        self.assertEqual(row["landlord_rejection_reason"], "Not what I saw.")
        self.assertEqual(row["escalated_by"], "Tina Ray")
        self.assertEqual(row["title"], "Damp patch in the bedroom")

    def test_decided_cases_move_to_the_other_filters(self):
        evidence = self.submitted()
        self.reject(evidence)
        self.escalate(evidence, self.tina)
        case = ReviewRequest.objects.get(kind="DISPUTE")
        self.sign_in_as_admin(email="admin@example.com")
        self.admin_decides(case.pk, "approve")

        self.assertEqual(self.client.get(ADMIN_URL).data["count"], 0)
        self.assertEqual(self.client.get(f"{ADMIN_URL}?status=APPROVED").data["count"], 1)

    def test_a_landlord_is_refused(self):
        self.as_user(self.lou)

        self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
