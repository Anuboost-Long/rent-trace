from datetime import date

from maintenance.models import MaintenanceClosureProposal, MaintenanceIssue
from maintenance.tests.base import MaintenanceApiTestCase
from notifications.models import Notification
from tenancies.models import Tenancy, TenancyParty


class ClosureTests(MaintenanceApiTestCase):
    def kinds_for(self, person):
        return [row.kind for row in Notification.objects.filter(recipient=person).order_by("id")]

    def issue_row(self):
        return MaintenanceIssue.objects.get()

    def test_a_tenant_proposes_and_the_landlord_approves(self):
        issue = self.reported()
        self.act(issue, "acknowledge/", self.lou)
        proposed = self.propose(issue, self.tina, "FIXED", "The tap is fixed.")

        self.assertEqual(proposed.status_code, 200, proposed.data)
        self.assertEqual(proposed.data["status"], "ACKNOWLEDGED")
        self.assertEqual(proposed.data["open_closure"]["proposer_side"], "TENANT")
        self.assertEqual(proposed.data["actions"], ["WITHDRAW_CLOSURE"])
        self.assertEqual(
            self.detail(issue, self.lou).data["actions"], ["APPROVE_CLOSURE", "REJECT_CLOSURE"]
        )

        approved = self.answer(issue, self.lou)

        self.assertEqual(approved.status_code, 200, approved.data)
        saved = self.issue_row()
        self.assertEqual((saved.status, saved.closure_outcome), ("CLOSED", "FIXED"))
        self.assertIsNotNone(saved.closed_at)
        self.assertIsNone(saved.open_closure_proposal)
        last = saved.status_history.order_by("sequence_no").last()
        self.assertEqual(
            (last.to_status, last.trigger, last.reason),
            ("CLOSED", "APPROVED_CLOSURE", "The tap is fixed."),
        )
        self.assertEqual(last.closure_proposal.proposed_by, self.tina)
        self.assertEqual(last.closure_proposal.response.decision, "APPROVED")
        self.assertEqual(
            self.kinds_for(self.lou)[-2:], ["MAINTENANCE_REPORTED", "MAINTENANCE_CLOSURE_PROPOSED"]
        )
        self.assertEqual(self.kinds_for(self.tina)[-1], "MAINTENANCE_CLOSED")
        self.assertEqual(approved.data["actions"], [])

    def test_a_landlord_proposes_and_any_current_tenant_can_approve(self):
        self.add_co_tenant()
        issue = self.reported()
        self.propose(issue, self.lou, "FIXED", "Plumber came.")

        self.assertEqual(self.kinds_for(self.sam)[-1], "MAINTENANCE_CLOSURE_PROPOSED")
        approved = self.answer(issue, self.sam)

        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertEqual(self.issue_row().status, "CLOSED")

    def test_closing_as_not_fixed_records_that_outcome(self):
        issue = self.reported()
        self.propose(issue, self.lou, "NOT_FIXED_NO_ACTION", "It is wear and tear.")
        self.answer(issue, self.tina)

        self.assertEqual(self.issue_row().closure_outcome, "NOT_FIXED_NO_ACTION")

    def test_a_rejection_keeps_it_open_and_tells_the_proposer(self):
        issue = self.reported()
        self.propose(issue, self.tina)

        rejected = self.answer(issue, self.lou, "reject")

        self.assertEqual(rejected.status_code, 200, rejected.data)
        saved = self.issue_row()
        self.assertEqual(saved.status, "REPORTED")
        self.assertIsNone(saved.open_closure_proposal)
        self.assertEqual(MaintenanceClosureProposal.objects.get().response.decision, "REJECTED")
        self.assertEqual(self.kinds_for(self.tina)[-1], "MAINTENANCE_CLOSURE_REJECTED")
        self.assertEqual(self.propose(issue, self.tina).status_code, 200)

    def test_you_cannot_answer_your_own_proposal_or_one_from_your_own_side(self):
        self.add_co_tenant()
        issue = self.reported()
        self.propose(issue, self.tina)

        proposal = self.detail(issue, self.tina).data["open_closure"]
        own = self.act(issue, f"closure/{proposal['id']}/approve/", self.tina)
        same_side = self.act(issue, f"closure/{proposal['id']}/approve/", self.sam)

        self.assertEqual((own.status_code, same_side.status_code), (403, 403))
        self.assertEqual(self.issue_row().status, "REPORTED")

    def test_a_stranger_cannot_answer(self):
        issue = self.reported()
        self.propose(issue, self.tina)
        proposal = self.detail(issue, self.tina).data["open_closure"]

        self.assertEqual(
            self.act(issue, f"closure/{proposal['id']}/approve/", self.amy).status_code, 404
        )

    def test_only_the_proposer_can_withdraw(self):
        issue = self.reported()
        self.propose(issue, self.tina)

        self.assertEqual(self.act(issue, "closure/withdraw/", self.lou).status_code, 403)
        withdrawn = self.act(issue, "closure/withdraw/", self.tina)

        self.assertEqual(withdrawn.status_code, 200, withdrawn.data)
        self.assertEqual(MaintenanceClosureProposal.objects.get().response.decision, "WITHDRAWN")
        self.assertEqual(self.act(issue, "closure/withdraw/", self.tina).status_code, 400)

    def test_only_one_proposal_is_open_at_a_time(self):
        issue = self.reported()
        self.propose(issue, self.tina)

        self.assertEqual(self.propose(issue, self.lou).status_code, 400)
        self.assertEqual(MaintenanceClosureProposal.objects.count(), 1)

    def test_a_stale_proposal_is_refused_not_applied(self):
        issue = self.reported()
        self.propose(issue, self.tina)
        MaintenanceIssue.objects.update(row_version=99)

        refused = self.answer(issue, self.lou)

        self.assertEqual(refused.status_code, 400)
        self.assertEqual(self.issue_row().status, "REPORTED")

    def test_a_wrong_or_old_proposal_id_is_refused(self):
        issue = self.reported()
        self.propose(issue, self.tina)
        proposal = self.detail(issue, self.tina).data["open_closure"]
        self.act(issue, "closure/withdraw/", self.tina)

        self.assertEqual(
            self.act(issue, f"closure/{proposal['id']}/approve/", self.lou).status_code, 400
        )
        self.assertEqual(self.act(issue, "closure/9999/reject/", self.lou).status_code, 400)

    def test_a_closed_issue_takes_nothing_more(self):
        issue = self.reported()
        self.propose(issue, self.tina)
        self.answer(issue, self.lou)

        for path in ("acknowledge/", "start/"):
            self.assertEqual(self.act(issue, path, self.lou).status_code, 400)
        self.assertEqual(self.propose(issue, self.tina).status_code, 400)

    def test_the_reason_and_outcome_are_required(self):
        issue = self.reported()

        self.assertEqual(
            self.act(issue, "closure/", self.tina, {"outcome": "FIXED"}).status_code, 400
        )
        self.assertEqual(
            self.act(issue, "closure/", self.tina, {"outcome": "MAYBE", "reason": "x"}).status_code,
            400,
        )
        self.assertEqual(
            self.act(issue, "closure/", self.tina, {"outcome": "FIXED", "reason": ""}).status_code,
            400,
        )


class CloseVacantTests(MaintenanceApiTestCase):
    def empty_the_tenancy(self):
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="ENDED")
        TenancyParty.objects.update(left_at=date(2026, 12, 20))

    def test_the_landlord_closes_directly_when_no_tenant_is_left(self):
        issue = self.reported()
        self.empty_the_tenancy()

        self.assertIn("CLOSE_VACANT", self.detail(issue, self.lou).data["actions"])
        closed = self.act(
            issue,
            "close/",
            self.lou,
            {"outcome": "NOT_FIXED_NO_ACTION", "reason": "Tenant moved out."},
        )

        self.assertEqual(closed.status_code, 200, closed.data)
        saved = MaintenanceIssue.objects.get()
        self.assertEqual((saved.status, saved.closure_outcome), ("CLOSED", "NOT_FIXED_NO_ACTION"))
        last = saved.status_history.order_by("sequence_no").last()
        self.assertEqual((last.trigger, last.actor), ("VACANT_OWNER_CLOSURE", self.lou))
        self.assertEqual(
            Notification.objects.filter(recipient=self.tina).last().kind, "MAINTENANCE_CLOSED"
        )

    def test_it_is_refused_while_a_tenant_still_lives_there(self):
        issue = self.reported()

        refused = self.act(issue, "close/", self.lou, {"outcome": "FIXED", "reason": "Done."})

        self.assertEqual(refused.status_code, 400)
        self.assertEqual(MaintenanceIssue.objects.get().status, "REPORTED")
        self.assertNotIn("CLOSE_VACANT", self.detail(issue, self.lou).data["actions"])

    def test_a_tenant_cannot_use_it(self):
        issue = self.reported()
        self.empty_the_tenancy()

        self.assertEqual(
            self.act(issue, "close/", self.tina, {"outcome": "FIXED", "reason": "x"}).status_code,
            403,
        )

    def test_an_open_proposal_is_withdrawn_when_the_landlord_closes_directly(self):
        issue = self.reported()
        self.propose(issue, self.lou)
        self.empty_the_tenancy()

        self.act(issue, "close/", self.lou, {"outcome": "FIXED", "reason": "Done."})

        saved = MaintenanceIssue.objects.get()
        self.assertEqual(saved.status, "CLOSED")
        self.assertIsNone(saved.open_closure_proposal)
        self.assertEqual(MaintenanceClosureProposal.objects.get().response.decision, "WITHDRAWN")
