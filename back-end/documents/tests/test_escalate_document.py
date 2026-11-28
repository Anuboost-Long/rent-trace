import uuid
from datetime import timedelta

from django.utils import timezone

from documents.models import Document
from documents.tests.base import LANDLORD_URL, DocumentApiTestCase
from history.models import BusinessChangeHistory
from notifications.models import Notification
from reviews.models import DisputeResolution, ReviewRequest, ReviewStatus

ADMIN_CASES = "/api/admin/documents/cases/"
REVIEW_CASES = "/api/admin/review-cases/"


class EscalateDocumentTests(DocumentApiTestCase):
    def setUp(self):
        super().setUp()
        self.admin = self.sign_in_as_admin(email="admin@example.com")
        self.document = self.published()
        self.version_id = self.document["versions"][0]["id"]

    def tenant_escalates(self, reason="This is wrong and we cannot agree.", version_id=None):
        self.as_user(self.tina)
        return self.post(
            f"{self.tenant_url}versions/{version_id or self.version_id}/escalate/",
            {"reason": reason},
        )

    def landlord_escalates(self, reason="They flagged it without cause.", version_id=None):
        self.as_user(self.lou)
        return self.post(
            f"{LANDLORD_URL}{self.document['id']}/versions/{version_id or self.version_id}/escalate/",
            {"reason": reason},
        )

    def flagged(self):
        self.assertEqual(
            self.answer(self.version_id, "flag", reason="The rent is wrong.").status_code, 200
        )

    def go_stale(self):
        ReviewRequest.objects.update(submitted_at=timezone.now() - timedelta(days=15))

    def decide(self, case_id, action="approve", reason="Checked the agreement.", key=None):
        self.as_user(self.admin)
        return self.post(
            f"{ADMIN_CASES}{case_id}/{action}/",
            {"idempotency_key": str(key or uuid.uuid4()), "reason": reason},
        )

    def case(self):
        return ReviewRequest.objects.document_cases().get()

    def test_a_tenant_sends_a_flagged_version_to_an_admin(self):
        self.flagged()

        response = self.tenant_escalates()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["versions"][0]["confirmation"], "ESCALATED")
        self.assertEqual(self.case().requester_side, "TENANT")
        self.assertTrue(
            Notification.objects.filter(recipient=self.admin, kind="DOCUMENT_ESCALATED")
        )
        self.assertTrue(
            Notification.objects.filter(recipient=self.lou, kind="DOCUMENT_SENT_TO_ADMIN")
        )

    def test_a_landlord_sends_a_flagged_version_to_an_admin(self):
        self.flagged()

        response = self.landlord_escalates()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.case().requester_side, "LANDLORD")
        self.assertTrue(
            Notification.objects.filter(recipient=self.tina, kind="DOCUMENT_SENT_TO_ADMIN")
        )

    def test_the_landlord_can_send_an_expired_version(self):
        self.go_stale()

        response = self.landlord_escalates("Nobody answered in 14 days.")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["versions"][0]["confirmation"], "ESCALATED")

    def test_a_version_still_waiting_cannot_be_sent(self):
        self.assertEqual(self.tenant_escalates().status_code, 400)
        self.assertEqual(self.landlord_escalates().status_code, 400)

    def test_a_reason_is_required(self):
        self.flagged()

        self.assertEqual(self.tenant_escalates(reason="  ").status_code, 400)

    def test_it_can_only_be_sent_once(self):
        self.flagged()
        self.tenant_escalates()

        self.assertEqual(self.landlord_escalates().status_code, 400)

    def test_an_older_version_cannot_be_sent_once_a_newer_one_exists(self):
        self.flagged()
        self.add_version(self.document)

        self.assertEqual(self.tenant_escalates().status_code, 400)

    def test_people_outside_the_tenancy_get_a_404(self):
        self.flagged()
        self.as_user(self.sam)
        stranger = self.post(
            f"{self.tenant_url}versions/{self.version_id}/escalate/", {"reason": "Nope"}
        )
        self.as_user(self.mia)
        other_landlord = self.post(
            f"{LANDLORD_URL}{self.document['id']}/versions/{self.version_id}/escalate/",
            {"reason": "Nope"},
        )

        self.assertEqual(stranger.status_code, 404)
        self.assertEqual(other_landlord.status_code, 404)

    def test_an_admin_confirms_it_and_it_becomes_current(self):
        self.flagged()
        self.tenant_escalates()
        case = self.case()

        response = self.decide(case.pk)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "APPROVED")
        document = Document.objects.get()
        self.assertEqual(document.current_version_id, self.version_id)
        self.assertEqual(document.updated_by, self.admin)
        self.assertEqual(
            BusinessChangeHistory.objects.get(action="ADMIN_CONFIRM_DOCUMENT_VERSION").created_by,
            self.admin,
        )
        self.assertEqual(
            DisputeResolution.objects.get().result_document_version_id, self.version_id
        )
        self.as_user(self.tina)
        seen = self.client.get(f"{self.tenant_url}{self.document['id']}/")
        self.assertEqual(seen.data["versions"][0]["confirmation"], "CONFIRMED")
        self.assertTrue(Notification.objects.filter(recipient=self.lou, kind="DOCUMENT_DECIDED"))
        self.assertTrue(Notification.objects.filter(recipient=self.tina, kind="DOCUMENT_DECIDED"))

    def test_an_admin_upholds_the_flag_and_nothing_becomes_current(self):
        self.flagged()
        self.landlord_escalates()

        response = self.decide(self.case().pk, "reject", reason="The rent really is wrong.")

        self.assertEqual(response.data["status"], "REJECTED")
        self.assertEqual(response.data["decision_reason"], "The rent really is wrong.")
        self.assertIsNone(Document.objects.get().current_version)
        self.as_user(self.tina)
        seen = self.client.get(f"{self.tenant_url}{self.document['id']}/")
        self.assertEqual(seen.data["versions"][0]["confirmation"], "FLAGGED")
        self.assertEqual(self.tenant_escalates().status_code, 400)

    def test_an_answer_sent_twice_changes_nothing(self):
        self.flagged()
        self.tenant_escalates()
        case = self.case()
        key = uuid.uuid4()
        self.decide(case.pk, key=key)

        again = self.decide(case.pk, key=key)
        other_key = self.decide(case.pk)

        self.assertEqual(again.status_code, 200)
        self.assertEqual(other_key.status_code, 400)
        self.assertEqual(BusinessChangeHistory.objects.count(), 1)

    def test_a_newer_version_closes_the_open_case(self):
        self.flagged()
        self.tenant_escalates()
        case = self.case()

        self.add_version(self.document)

        case.refresh_from_db()
        self.assertEqual(case.status, ReviewStatus.CANCELLED)
        self.assertEqual(self.decide(case.pk).status_code, 400)
        self.assertIsNone(Document.objects.get().current_version)

    def test_the_admin_queue_lists_waiting_cases_and_filters_by_status(self):
        self.flagged()
        self.tenant_escalates()
        self.as_user(self.admin)

        waiting = self.client.get(ADMIN_CASES)
        decided = self.client.get(f"{ADMIN_CASES}?status=APPROVED")

        self.assertEqual(waiting.status_code, 200, waiting.data)
        item = waiting.data["results"][0]
        self.assertEqual(
            (item["title"], item["raised_by_side"], item["flag_reason"], item["version_no"]),
            ("Tenancy agreement", "TENANT", "The rent is wrong.", 1),
        )
        self.assertEqual(item["reason"], "This is wrong and we cannot agree.")
        self.assertEqual(decided.data["count"], 0)

    def test_condition_cases_never_show_a_document_case_and_still_work(self):
        self.flagged()
        self.tenant_escalates()
        self.as_user(self.admin)

        listed = self.client.get(REVIEW_CASES)

        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertEqual(listed.data["count"], 0)
        refused = self.post(
            f"{REVIEW_CASES}{self.case().pk}/approve/",
            {"idempotency_key": str(uuid.uuid4()), "reason": "x"},
        )
        self.assertEqual(refused.status_code, 404)

    def test_only_admins_with_the_review_permission_can_use_the_queue(self):
        self.as_user(self.lou)

        self.assertEqual(self.client.get(ADMIN_CASES).status_code, 403)
