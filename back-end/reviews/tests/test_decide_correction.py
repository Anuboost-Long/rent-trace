import uuid

from conditions.models import ConditionRecord
from history.models import BusinessChangeHistory
from notifications.models import Notification
from reviews.models import ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class DecideCorrectionTests(EvidenceApiTestCase):
    def asked(self, sign_in_admin=True):
        note = self.shown_note()
        request_id = self.ask_tenant_correction(note["id"]).data["id"]
        if sign_in_admin:
            self.sign_in_as_admin(email="admin@example.com")
        return note, request_id

    def test_approving_makes_the_corrected_wording_the_accepted_version(self):
        note, request_id = self.asked()

        response = self.decide_correction(request_id, "approve")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "APPROVED")
        self.assertEqual(response.data["admin_reason"], "Checked the inspection report.")
        record = ConditionRecord.objects.get(pk=note["id"])
        self.assertEqual(record.accepted_version.version_no, 2)
        self.assertEqual(
            record.accepted_version.condition_description, "Benchtop in good condition."
        )
        self.assertEqual(record.accepted_version.supersedes_version.version_no, 1)
        history = BusinessChangeHistory.objects.get(action="ACCEPT_CONDITION_VERSION")
        self.assertEqual(
            (history.before_values, history.after_values),
            ({"accepted_version": 1}, {"accepted_version": 2}),
        )

    def test_rejecting_changes_nothing_and_a_reason_is_required_both_ways(self):
        note, request_id = self.asked()

        self.assertEqual(self.decide_correction(request_id, "reject", reason="  ").status_code, 400)
        response = self.decide_correction(request_id, "reject", reason="The chip is in the report.")

        self.assertEqual(response.data["status"], "REJECTED")
        self.assertEqual(ConditionRecord.objects.get(pk=note["id"]).accepted_version.version_no, 1)

    def test_a_correction_is_decided_once_and_a_retry_changes_nothing(self):
        _, request_id = self.asked()
        key = uuid.uuid4()
        self.decide_correction(request_id, "approve", key=key)

        self.assertEqual(self.decide_correction(request_id, "approve", key=key).status_code, 200)
        self.assertEqual(self.decide_correction(request_id, "reject").status_code, 400)
        self.assertEqual(BusinessChangeHistory.objects.count(), 1)

    def test_a_note_edited_after_the_request_makes_it_stale(self):
        note, request_id = self.asked(sign_in_admin=False)
        self.as_user(self.lou)
        edited = self.client.patch(
            f"/api/landlord/conditions/{note['id']}/", {"title": "Benchtop (edited)"}, format="json"
        )
        self.assertEqual(edited.status_code, 200, edited.data)
        self.sign_in_as_admin(email="admin@example.com")

        response = self.decide_correction(request_id, "approve")

        self.assertEqual(response.data["status"], "STALE")
        self.assertEqual(
            ConditionRecord.objects.get(pk=note["id"]).accepted_version.title, "Benchtop (edited)"
        )

    def test_the_asker_and_the_owners_are_told(self):
        _, request_id = self.asked()

        self.decide_correction(request_id, "approve")

        told = Notification.objects.filter(kind="CONDITION_CORRECTION_DECIDED")
        self.assertEqual({n.recipient for n in told}, {self.tina, self.lou})

    def test_the_asker_can_withdraw_it_until_it_is_decided(self):
        note = self.shown_note()
        request_id = self.ask_tenant_correction(note["id"]).data["id"]
        url = (
            f"/api/tenant/tenancies/{self.tenancy['id']}/condition-corrections/{request_id}/cancel/"
        )

        self.assertEqual(self.post(url).data["status"], "CANCELLED")
        self.assertEqual(self.post(url).status_code, 400)
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(self.decide_correction(request_id, "approve").status_code, 400)
        self.assertEqual(ReviewRequest.objects.get().status, "CANCELLED")

    def test_only_an_admin_with_the_permission_can_decide(self):
        _, request_id = self.asked()
        self.as_user(self.lou)

        self.assertEqual(self.decide_correction(request_id, "approve").status_code, 403)
