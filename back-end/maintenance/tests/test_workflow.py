from maintenance.models import MaintenanceIssue
from maintenance.tests.base import MaintenanceApiTestCase
from notifications.models import Notification


class WorkflowTests(MaintenanceApiTestCase):
    def kinds_for(self, person):
        return [row.kind for row in Notification.objects.filter(recipient=person).order_by("id")]

    def test_the_landlord_acknowledges_then_starts_work(self):
        issue = self.reported()

        acknowledged = self.act(issue, "acknowledge/", self.lou)
        started = self.act(issue, "start/", self.lou)

        self.assertEqual(acknowledged.status_code, 200, acknowledged.data)
        self.assertEqual(acknowledged.data["status"], "ACKNOWLEDGED")
        self.assertEqual(started.data["status"], "IN_PROGRESS")
        saved = MaintenanceIssue.objects.get()
        self.assertIsNotNone(saved.acknowledged_at)
        self.assertIsNotNone(saved.work_started_at)
        history = [
            (h.sequence_no, h.to_status, h.trigger)
            for h in saved.status_history.order_by("sequence_no")
        ]
        self.assertEqual(
            history,
            [
                (1, "REPORTED", "REPORT"),
                (2, "ACKNOWLEDGED", "OPPOSITE_OPEN"),
                (3, "IN_PROGRESS", "CONFIRM_START"),
            ],
        )
        self.assertEqual(
            self.kinds_for(self.tina), ["MAINTENANCE_ACKNOWLEDGED", "MAINTENANCE_STARTED"]
        )

    def test_the_steps_have_to_come_in_order(self):
        issue = self.reported()

        self.assertEqual(self.act(issue, "start/", self.lou).status_code, 400)
        self.act(issue, "acknowledge/", self.lou)
        self.assertEqual(self.act(issue, "acknowledge/", self.lou).status_code, 400)
        self.act(issue, "start/", self.lou)
        self.assertEqual(self.act(issue, "start/", self.lou).status_code, 400)
        self.assertEqual(MaintenanceIssue.objects.get().status, "IN_PROGRESS")

    def test_a_tenant_or_a_stranger_cannot_acknowledge_or_start(self):
        issue = self.reported()

        self.assertEqual(self.act(issue, "acknowledge/", self.tina).status_code, 403)
        self.assertEqual(self.act(issue, "acknowledge/", self.amy).status_code, 404)
        self.assertEqual(self.act(issue, "start/", self.sam).status_code, 404)
        self.assertEqual(MaintenanceIssue.objects.get().status, "REPORTED")

    def test_nothing_moves_while_a_closure_proposal_waits(self):
        issue = self.reported()
        self.propose(issue, self.tina)

        refused = self.act(issue, "acknowledge/", self.lou)

        self.assertEqual(refused.status_code, 400)
        self.assertIn("closure", str(refused.data).lower())

    def test_notifications_carry_the_title_and_no_contact_details(self):
        issue = self.reported()
        self.act(issue, "acknowledge/", self.lou)

        text = " ".join(row.title + row.body for row in Notification.objects.all())

        self.assertIn("Kitchen tap drips", text)
        self.assertNotIn("@example.com", text)
