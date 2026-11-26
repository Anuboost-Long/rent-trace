from notifications.models import Notification
from reviews.models import RemovalRequestItem, ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class RequestRemovalTests(EvidenceApiTestCase):
    def test_a_tenant_asks_an_admin_to_hide_their_own_report(self):
        evidence = self.submitted()
        record = self.record_of(evidence)
        admin = self.sign_in_as_admin(email="admin@example.com")

        response = self.ask_tenant_removal([record])

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["status"], "PENDING_REVIEW")
        self.assertEqual(response.data["items"][0]["record_id"], record)
        self.assertEqual(response.data["reason"], "Entered by mistake.")
        request = ReviewRequest.objects.get(kind="DATA_REMOVAL")
        self.assertEqual((request.review_route, request.requester_side), ("ADMIN", "TENANT"))
        self.assertEqual(RemovalRequestItem.objects.get().include_descendants, True)
        sent = Notification.objects.get(recipient=admin, kind="DATA_REMOVAL_REQUESTED")
        self.assertEqual(sent.subject_id, request.pk)

    def test_a_landlord_asks_to_hide_any_record_on_their_property(self):
        note = self.shown_note()
        evidence = self.submitted()

        response = self.ask_landlord_removal([note["id"], self.record_of(evidence)])

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(len(response.data["items"]), 2)
        self.assertEqual(response.data["requester_side"], "LANDLORD")

    def test_records_you_may_not_remove_are_a_404(self):
        evidence = self.submitted()
        note = self.shown_note()
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(
            self.ask_tenant_removal([self.record_of(evidence)], user=self.sam).status_code, 404
        )
        self.assertEqual(self.ask_tenant_removal([note["id"]]).status_code, 404)
        self.assertEqual(
            self.ask_landlord_removal([self.record_of(evidence)], user=self.mia).status_code, 404
        )
        self.assertEqual(self.ask_tenant_removal([9999]).status_code, 404)

    def test_a_reason_and_between_one_and_twenty_records_are_required(self):
        record = self.record_of(self.submitted())

        self.assertEqual(self.ask_tenant_removal([record], reason="  ").status_code, 400)
        self.assertEqual(self.ask_tenant_removal([]).status_code, 400)
        self.assertEqual(self.ask_tenant_removal(list(range(1, 22))).status_code, 400)

    def test_a_record_with_a_waiting_removal_cannot_be_asked_again(self):
        record = self.record_of(self.submitted())
        self.ask_tenant_removal([record])

        self.assertEqual(self.ask_tenant_removal([record]).status_code, 400)
        self.assertEqual(self.ask_landlord_removal([record]).status_code, 400)
