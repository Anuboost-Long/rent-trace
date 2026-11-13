from datetime import date

from django.utils import timezone

from maintenance.models import MaintenanceIssue
from maintenance.tests.base import URL, MaintenanceApiTestCase
from notifications.models import Notification
from tenancies.models import Tenancy, TenancyParty


class ReportAndScopeTests(MaintenanceApiTestCase):
    def test_a_tenant_reports_an_issue_and_the_landlord_is_told(self):
        response = self.report()

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(
            (response.data["status"], response.data["priority"], response.data["my_side"]),
            ("REPORTED", "MEDIUM", "TENANT"),
        )
        issue = MaintenanceIssue.objects.get()
        self.assertEqual((issue.reported_by, issue.reporter_side), (self.tina, "TENANT"))
        self.assertEqual(issue.property_unit_id, self.unit.pk)
        (history,) = issue.status_history.all()
        self.assertEqual(
            (history.sequence_no, history.to_status, history.trigger), (1, "REPORTED", "REPORT")
        )
        (note,) = Notification.objects.filter(recipient=self.lou)
        self.assertEqual(note.kind, "MAINTENANCE_REPORTED")
        self.assertEqual(note.subject_id, issue.pk)
        self.assertNotIn("tina@example.com", note.title + note.body)

    def test_the_title_description_and_priority_are_checked(self):
        for extra in (
            {"title": ""},
            {"description": ""},
            {"priority": "WHENEVER"},
            {"title": "x" * 201},
        ):
            with self.subTest(extra=extra):
                self.assertEqual(self.report(**extra).status_code, 400)
        self.assertFalse(MaintenanceIssue.objects.exists())

    def test_only_a_current_tenant_of_an_active_tenancy_can_report(self):
        self.assertEqual(self.report(user=self.sam).status_code, 404)
        self.assertEqual(self.report(user=self.lou).status_code, 404)
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="DRAFT")
        self.assertEqual(self.report().status_code, 400)
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="ENDED")
        self.assertEqual(self.report().status_code, 400)
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="ACTIVE")
        TenancyParty.objects.filter(tenant=self.tina).update(left_at=date(2026, 12, 20))
        self.assertEqual(self.report().status_code, 404)

    def test_admins_and_signed_out_visitors_are_refused(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.get(URL).status_code, 401)

    def test_each_side_sees_only_its_own_issues(self):
        issue = self.reported()

        self.as_user(self.tina)
        self.assertEqual([row["id"] for row in self.client.get(URL).data["results"]], [issue["id"]])
        self.as_user(self.lou)
        self.assertEqual([row["id"] for row in self.client.get(URL).data["results"]], [issue["id"]])
        for stranger in (self.sam, self.amy):
            self.as_user(stranger)
            self.assertEqual(self.client.get(URL).data["count"], 0)
            self.assertEqual(self.client.get(f"{URL}{issue['id']}/").status_code, 404)

    def test_the_list_filters_by_status_and_is_newest_first(self):
        first = self.reported(title="First")
        second = self.reported(title="Second")
        MaintenanceIssue.objects.filter(pk=first["id"]).update(
            status="ACKNOWLEDGED", acknowledged_at=timezone.now()
        )

        self.as_user(self.lou)
        everything = [row["id"] for row in self.client.get(URL).data["results"]]
        reported = [
            row["id"] for row in self.client.get(URL, {"status": "REPORTED"}).data["results"]
        ]

        self.assertEqual(everything, [second["id"], first["id"]])
        self.assertEqual(reported, [second["id"]])
        self.assertEqual(self.client.get(URL, {"status": "NOPE"}).status_code, 400)

    def test_someone_who_left_can_still_read_but_not_act(self):
        issue = self.reported()
        TenancyParty.objects.filter(tenant=self.tina).update(left_at=date(2026, 12, 20))

        response = self.detail(issue, self.tina)

        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.data["actions"], response.data["my_side"]), ([], None))
        self.assertEqual(self.propose(issue, self.tina).status_code, 403)

    def test_the_detail_lists_the_history_and_what_the_viewer_can_do(self):
        issue = self.reported()

        tenant = self.detail(issue, self.tina).data
        landlord = self.detail(issue, self.lou).data

        self.assertEqual(tenant["actions"], ["PROPOSE_CLOSURE"])
        self.assertEqual(landlord["actions"], ["ACKNOWLEDGE", "ASSIGN_PROVIDER", "PROPOSE_CLOSURE"])
        self.assertEqual([h["to_status"] for h in tenant["history"]], ["REPORTED"])
        self.assertEqual(tenant["history"][0]["actor"], "Tina Ray")
