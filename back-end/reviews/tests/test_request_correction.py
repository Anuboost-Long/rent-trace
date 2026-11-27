from conditions.models import ConditionRecord
from notifications.models import Notification
from reviews.models import ReviewRequest
from reviews.tests.base import EvidenceApiTestCase


class RequestCorrectionTests(EvidenceApiTestCase):
    def test_a_tenant_asks_an_admin_to_correct_a_shown_note_and_nothing_changes_yet(self):
        note = self.shown_note()
        admin = self.sign_in_as_admin(email="admin@example.com")

        response = self.ask_tenant_correction(note["id"])

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["status"], "PENDING_REVIEW")
        self.assertEqual(response.data["requester_side"], "TENANT")
        self.assertEqual(response.data["current_title"], "Kitchen benchtop")
        self.assertEqual(response.data["proposed_description"], "Benchtop in good condition.")
        request = ReviewRequest.objects.get()
        self.assertEqual((request.kind, request.review_route), ("LOCKED_CORRECTION", "ADMIN"))
        self.assertEqual(ConditionRecord.objects.get().versions.count(), 1)
        sent = Notification.objects.get(recipient=admin, kind="CONDITION_CORRECTION_REQUESTED")
        self.assertEqual(sent.subject_id, request.pk)

    def test_the_landlord_asks_to_correct_an_approved_tenant_report(self):
        evidence = self.submitted()
        self.approve(evidence)
        record = ReviewRequest.objects.get().target.condition_record_id

        self.as_user(self.lou)
        response = self.post("/api/landlord/condition-corrections/", self.correction_fields(record))

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["requester_side"], "LANDLORD")

    def test_a_note_that_is_not_shown_or_not_on_the_unit_is_a_404(self):
        self.as_user(self.lou)
        hidden = self.post(
            "/api/landlord/conditions/",
            {
                "unit_id": self.unit.pk,
                "title": "Hidden",
                "observed_at": "2026-11-13T00:00:00Z",
            },
        )

        self.assertEqual(self.ask_tenant_correction(hidden.data["id"]).status_code, 404)
        self.assertEqual(self.ask_tenant_correction(9999).status_code, 404)

    def test_a_pending_report_or_a_landlord_note_is_not_correctable_by_the_landlord(self):
        note = self.shown_note()
        self.as_user(self.lou)

        waiting = self.submitted()
        record = ReviewRequest.objects.get(pk=waiting["id"]).target.condition_record_id
        self.as_user(self.lou)
        self.assertEqual(
            self.post(
                "/api/landlord/condition-corrections/", self.correction_fields(note["id"])
            ).status_code,
            404,
        )
        self.assertEqual(
            self.post(
                "/api/landlord/condition-corrections/", self.correction_fields(record)
            ).status_code,
            404,
        )

    def test_only_one_correction_can_wait_per_note(self):
        note = self.shown_note()
        self.ask_tenant_correction(note["id"])
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(self.ask_tenant_correction(note["id"], user=self.sam).status_code, 400)

    def test_all_three_reasons_are_required(self):
        note = self.shown_note()

        for field in ("what_is_incorrect", "proposed_replacement", "why_change_needed"):
            response = self.ask_tenant_correction(note["id"], **{field: "  "})
            self.assertEqual(response.status_code, 400, field)

    def test_a_stranger_and_a_landlord_of_another_property_are_refused(self):
        note = self.shown_note()
        outsider = self.make_user("out@example.com", "TENANT", "Out", "Sider")

        self.assertEqual(self.ask_tenant_correction(note["id"], user=outsider).status_code, 404)
        self.as_user(self.mia)
        self.assertEqual(
            self.post(
                "/api/landlord/condition-corrections/", self.correction_fields(note["id"])
            ).status_code,
            404,
        )
