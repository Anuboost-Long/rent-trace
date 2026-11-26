import uuid

from history.models import BusinessChangeHistory
from reviews.models import ReviewDecision, ReviewRequest
from reviews.tests.base import EvidenceApiTestCase

ADMIN_EVIDENCE = "/api/admin/condition-evidence/"


class SuperAdminActsTests(EvidenceApiTestCase):
    def act(self, evidence, action, **fields):
        return self.post(f"{ADMIN_EVIDENCE}{evidence['id']}/{action}/", fields)

    def key(self):
        return {"idempotency_key": str(uuid.uuid4())}

    def last_move(self):
        return ReviewRequest.objects.get(kind="EVIDENCE_REVIEW").status_history.latest(
            "sequence_no"
        )

    def test_a_super_admin_approves_for_the_primary_owner(self):
        evidence = self.submitted()
        boss = self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        response = self.act(evidence, "approve", **self.key())

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "APPROVED")
        move = self.last_move()
        self.assertEqual((move.actor, move.on_behalf_of), (boss, self.lou))
        decision = ReviewDecision.objects.get()
        self.assertEqual((decision.reviewer, decision.reviewer_side), (boss, "LANDLORD"))
        change = BusinessChangeHistory.objects.get(action="ACCEPT_CONDITION_VERSION")
        self.assertEqual((change.created_by, change.on_behalf_of), (boss, self.lou))

    def test_rejecting_for_the_owner_opens_the_dispute_and_records_who_it_was_for(self):
        evidence = self.submitted()
        boss = self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        response = self.act(evidence, "reject", reason="Not what the owner saw.", **self.key())

        self.assertEqual(response.data["status"], "DISPUTED")
        case = ReviewRequest.objects.get(kind="DISPUTE")
        opened = case.status_history.get(action="OPEN_DISPUTE")
        self.assertEqual((opened.actor, opened.on_behalf_of), (boss, self.lou))

    def test_acting_for_the_tenant_records_the_author(self):
        evidence = self.submitted()
        boss = self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.act(evidence, "request-information", reason="Which wall?", **self.key())
        self.assertEqual(self.last_move().on_behalf_of, self.lou)

        answered = self.act(evidence, "respond", message="The north wall.")

        self.assertEqual(answered.data["status"], "PENDING_REVIEW")
        move = self.last_move()
        self.assertEqual((move.actor, move.on_behalf_of, move.action), (boss, self.tina, "RESPOND"))
        withdrawn = self.act(evidence, "cancel")
        self.assertEqual(withdrawn.data["status"], "CANCELLED")
        self.assertEqual(self.last_move().on_behalf_of, self.tina)

    def test_the_normal_rules_still_apply(self):
        evidence = self.submitted()
        self.expire(evidence)
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        self.assertEqual(self.act(evidence, "approve", **self.key()).status_code, 400)
        self.assertEqual(self.act(evidence, "respond", message="x").status_code, 400)

    def test_a_retry_with_the_same_key_changes_nothing(self):
        evidence = self.submitted()
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        key = self.key()
        self.act(evidence, "approve", **key)

        self.assertEqual(self.act(evidence, "approve", **key).status_code, 200)
        self.assertEqual(BusinessChangeHistory.objects.count(), 1)

    def test_a_regular_admin_a_landlord_and_a_tenant_are_refused(self):
        evidence = self.submitted()
        self.as_user(self.lou)
        self.assertEqual(self.act(evidence, "approve", **self.key()).status_code, 403)
        self.as_user(self.tina)
        self.assertEqual(self.act(evidence, "cancel").status_code, 403)
        self.sign_in_as_admin(email="plain@example.com")
        self.assertEqual(self.act(evidence, "approve", **self.key()).status_code, 403)

    def test_an_admin_lists_the_reports_on_a_unit(self):
        self.submitted()
        self.sign_in_as_admin(email="plain@example.com")

        listed = self.client.get(f"{ADMIN_EVIDENCE}?unit_id={self.unit.pk}")

        self.assertEqual(listed.status_code, 200)
        self.assertEqual([r["author"] for r in listed.data], ["Tina Ray"])
