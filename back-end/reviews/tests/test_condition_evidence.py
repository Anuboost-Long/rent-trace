import uuid

from conditions.models import ConditionRecord
from history.models import BusinessChangeHistory
from notifications.models import Notification
from reviews.models import Dispute, ReviewRequest
from tenancies.tests.base import TenancyApiTestCase

LANDLORD_URL = "/api/landlord/condition-evidence/"


class ConditionEvidenceTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.add_tenant(self.tenancy["id"], self.tina)
        self.mia = self.make_user("mia@example.com", "LANDLORD", "Mia", "Cole")
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")

    @property
    def tenant_url(self):
        return f"/api/tenant/tenancies/{self.tenancy['id']}/condition-evidence/"

    def evidence_fields(self, **extra):
        return {
            "title": "Damp patch in the bedroom",
            "description": "Wall near the window.",
            "observed_at": "2026-12-02T00:00:00Z",
            **extra,
        }

    def submit(self, user=None, **extra):
        self.as_user(user or self.tina)
        return self.post(self.tenant_url, self.evidence_fields(**extra))

    def submitted(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def approve(self, evidence, user=None, key=None):
        self.as_user(user or self.lou)
        return self.post(
            f"{LANDLORD_URL}{evidence['id']}/approve/",
            {"idempotency_key": str(key or uuid.uuid4())},
        )

    def reject(self, evidence, user=None, key=None, **extra):
        self.as_user(user or self.lou)
        payload = {
            "idempotency_key": str(key or uuid.uuid4()),
            "reason": "Not what I saw.",
            **extra,
        }
        return self.post(f"{LANDLORD_URL}{evidence['id']}/reject/", payload)

    def test_a_tenant_adds_an_account_that_waits_for_the_landlord(self):
        evidence = self.submitted()

        self.assertEqual(evidence["status"], "PENDING_REVIEW")
        self.assertEqual(evidence["title"], "Damp patch in the bedroom")
        note = ConditionRecord.objects.get(
            pk=ReviewRequest.objects.get().target.condition_record_id
        )
        self.assertEqual(note.record_type, "DISCREPANCY")
        self.assertIsNone(note.accepted_version)
        self.assertEqual(note.versions.get().source_type, "TENANT")
        self.assertEqual(
            list(ReviewRequest.objects.get().status_history.values_list("action", "to_status")),
            [("SUBMIT", "PENDING_REVIEW")],
        )

    def test_the_landlord_is_told_and_sees_it_on_the_unit(self):
        self.submitted()

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.lou, kind="CONDITION_EVIDENCE_SUBMITTED"
            ).exists()
        )
        self.as_user(self.lou)
        listed = self.client.get(f"{LANDLORD_URL}?unit_id={self.unit.pk}")
        self.assertEqual([row["author"] for row in listed.data], ["Tina Ray"])

    def test_someone_who_is_not_a_tenant_of_it_gets_a_404(self):
        self.assertEqual(self.submit(user=self.sam).status_code, 404)
        self.assertEqual(ReviewRequest.objects.count(), 0)

    def test_the_tenant_lists_only_their_own_accounts(self):
        self.submitted()
        self.add_tenant(self.tenancy["id"], self.sam)
        self.submit(user=self.sam, title="Cracked tile")

        self.as_user(self.tina)
        listed = self.client.get(self.tenant_url)

        self.assertEqual([row["title"] for row in listed.data], ["Damp patch in the bedroom"])

    def test_approving_makes_the_account_the_accepted_version_and_records_the_change(self):
        evidence = self.submitted()

        response = self.approve(evidence)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "APPROVED")
        request = ReviewRequest.objects.get()
        note = request.target.condition_record
        self.assertEqual(note.accepted_version_id, note.versions.get().pk)
        self.assertIsNotNone(request.applied_at)
        change = BusinessChangeHistory.objects.get()
        self.assertEqual(change.after_values, {"accepted_version": 1})
        self.assertEqual(
            list(request.status_history.values_list("action", flat=True)), ["SUBMIT", "APPROVE"]
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.tina, kind="CONDITION_EVIDENCE_APPROVED"
            ).exists()
        )

    def test_rejecting_needs_a_reason(self):
        evidence = self.submitted()

        response = self.reject(evidence, reason="  ")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ReviewRequest.objects.get().status, "PENDING_REVIEW")

    def test_rejecting_marks_it_disputed_and_opens_a_linked_dispute(self):
        evidence = self.submitted()

        response = self.reject(evidence)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "DISPUTED")
        self.assertEqual(response.data["rejection_reason"], "Not what I saw.")
        dispute = Dispute.objects.get()
        self.assertEqual(dispute.origin_request_id, evidence["id"])
        self.assertEqual(dispute.request.parent_request_id, evidence["id"])
        self.assertIsNone(
            ReviewRequest.objects.get(pk=evidence["id"]).target.condition_record.accepted_version
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.tina, kind="CONDITION_EVIDENCE_REJECTED"
            ).exists()
        )

    def test_a_tenant_cannot_answer_their_own_account(self):
        evidence = self.submitted()

        self.assertEqual(self.approve(evidence, user=self.tina).status_code, 403)
        self.assertEqual(ReviewRequest.objects.get().status, "PENDING_REVIEW")

    def test_another_landlord_gets_a_404(self):
        evidence = self.submitted()

        self.assertEqual(self.approve(evidence, user=self.mia).status_code, 404)

    def test_retrying_the_same_answer_changes_nothing(self):
        evidence = self.submitted()
        key = uuid.uuid4()
        self.approve(evidence, key=key)

        again = self.approve(evidence, key=key)

        self.assertEqual(again.status_code, 200, again.data)
        self.assertEqual(BusinessChangeHistory.objects.count(), 1)
        self.assertEqual(ReviewRequest.objects.get().decisions.count(), 1)

    def test_an_answered_account_cannot_be_answered_again(self):
        evidence = self.submitted()
        self.approve(evidence)

        self.assertEqual(self.reject(evidence).status_code, 400)

    def test_the_tenant_can_withdraw_it_until_it_is_answered(self):
        evidence = self.submitted()
        self.as_user(self.tina)

        cancelled = self.post(f"{self.tenant_url}{evidence['id']}/cancel/")

        self.assertEqual(cancelled.data["status"], "CANCELLED")
        self.assertEqual(self.approve(evidence).status_code, 400)

    def test_nobody_else_can_withdraw_it(self):
        evidence = self.submitted()
        self.add_tenant(self.tenancy["id"], self.sam)
        self.as_user(self.sam)

        self.assertEqual(self.post(f"{self.tenant_url}{evidence['id']}/cancel/").status_code, 404)
