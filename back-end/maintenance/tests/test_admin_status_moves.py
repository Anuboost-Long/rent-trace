from datetime import date

from django.utils import timezone

from maintenance.models import MaintenanceIssue
from maintenance.tests.base import MaintenanceApiTestCase
from properties.models import PropertyOwner
from tenancies.models import Tenancy, TenancyParty

ADMIN_URL = "/api/admin/maintenance/"


class AdminStatusMoveTests(MaintenanceApiTestCase):
    def sign_in_boss(self):
        return self.sign_in_as_admin(super_admin=True, email="boss@example.com")

    def move(self, issue, path, data=None):
        return self.post(f"{ADMIN_URL}{issue['id']}/{path}/", data or {})

    def last_history(self, issue):
        return (
            MaintenanceIssue.objects.get(pk=issue["id"])
            .status_history.order_by("sequence_no")
            .last()
        )

    def test_a_super_admin_acknowledges_and_starts_work_for_the_primary_owner(self):
        issue = self.reported()
        boss = self.sign_in_boss()

        acknowledged = self.move(issue, "acknowledge")
        row = self.last_history(issue)

        self.assertEqual(acknowledged.status_code, 200, acknowledged.data)
        self.assertEqual(acknowledged.data["status"], "ACKNOWLEDGED")
        self.assertEqual((row.actor, row.on_behalf_of), (boss, self.lou))

        started = self.move(issue, "start")
        row = self.last_history(issue)

        self.assertEqual(started.data["status"], "IN_PROGRESS")
        self.assertEqual((row.actor, row.on_behalf_of), (boss, self.lou))
        self.assertEqual(MaintenanceIssue.objects.get().updated_by, boss)

    def test_the_timeline_says_who_the_admin_acted_for(self):
        issue = self.reported()
        self.sign_in_boss()

        response = self.move(issue, "acknowledge")

        entry = response.data["history"][-1]
        self.assertEqual(entry["on_behalf_of"], "Lou Reed")
        self.assertNotEqual(entry["actor"], "Lou Reed")

    def test_a_super_admin_closes_directly_when_nobody_lives_there(self):
        issue = self.reported()
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="ENDED")
        TenancyParty.objects.update(left_at=date(2026, 12, 20))
        boss = self.sign_in_boss()

        closed = self.move(issue, "close", {"outcome": "NOT_FIXED_NO_ACTION", "reason": "Moved."})
        row = self.last_history(issue)

        self.assertEqual(closed.status_code, 200, closed.data)
        self.assertEqual(
            (row.trigger, row.actor, row.on_behalf_of), ("VACANT_OWNER_CLOSURE", boss, self.lou)
        )

    def test_closing_still_needs_the_tenants_while_someone_lives_there(self):
        issue = self.reported()
        self.sign_in_boss()

        response = self.move(issue, "close", {"outcome": "FIXED", "reason": "Done."})

        self.assertEqual(response.status_code, 400)

    def test_the_landlords_rules_still_apply(self):
        issue = self.reported()
        self.sign_in_boss()

        too_early = self.move(issue, "start")
        self.move(issue, "acknowledge")
        twice = self.move(issue, "acknowledge")

        self.assertEqual((too_early.status_code, twice.status_code), (400, 400))

    def test_the_detail_lists_the_landlords_moves_for_a_super_admin(self):
        issue = self.reported()
        self.sign_in_boss()

        reported = self.client.get(f"{ADMIN_URL}{issue['id']}/").data["actions"]
        self.move(issue, "acknowledge")
        acknowledged = self.client.get(f"{ADMIN_URL}{issue['id']}/").data["actions"]

        self.assertEqual(reported, ["ACKNOWLEDGE", "ASSIGN_PROVIDER", "PROPOSE_CLOSURE"])
        self.assertEqual(acknowledged, ["START", "ASSIGN_PROVIDER", "PROPOSE_CLOSURE"])

    def test_while_a_closing_proposal_waits_the_admin_can_only_answer_it(self):
        issue = self.reported()
        self.propose(issue, self.tina)
        self.sign_in_boss()

        self.assertEqual(
            self.client.get(f"{ADMIN_URL}{issue['id']}/").data["actions"],
            ["APPROVE_CLOSURE", "REJECT_CLOSURE"],
        )
        self.assertEqual(self.move(issue, "acknowledge").status_code, 400)

    def test_a_property_without_a_primary_owner_is_refused(self):
        issue = self.reported()
        PropertyOwner.objects.update(valid_to=timezone.now())
        self.sign_in_boss()

        response = self.move(issue, "acknowledge")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(MaintenanceIssue.objects.get().status, "REPORTED")

    def test_a_super_admin_who_is_the_landlord_records_nobody_as_acted_for(self):
        issue = self.reported()
        boss = self.sign_in_boss()
        PropertyOwner.objects.create(
            property_id=self.property["id"],
            owner=boss,
            ownership_percentage=50,
            valid_from=timezone.now(),
        )

        self.move(issue, "acknowledge")

        self.assertIsNone(self.last_history(issue).on_behalf_of)

    def test_a_normal_admin_landlords_and_tenants_are_refused(self):
        issue = self.reported()
        self.sign_in_as_admin(email="plain@example.com")
        results = [self.move(issue, "acknowledge").status_code]
        for user in (self.lou, self.tina):
            self.as_user(user)
            results.append(self.move(issue, "acknowledge").status_code)

        self.assertEqual(results, [403, 403, 403])
        self.assertEqual(MaintenanceIssue.objects.get().status, "REPORTED")
