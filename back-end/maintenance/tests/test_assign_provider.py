from maintenance.tests.base import URL, MaintenanceApiTestCase
from notifications.models import Notification
from providers.models import MaintenanceAssignment

PROVIDERS = "/api/landlord/providers/"


class AssignProviderTests(MaintenanceApiTestCase):
    def provider(self, name="Smith Plumbing", *, landlord=None, linked=True, **extra):
        self.as_user(landlord or self.lou)
        links = [{"property_id": self.property["id"], "is_recommended": False}] if linked else []
        response = self.post(
            PROVIDERS,
            {
                "business_name": name,
                "phone_number": "0400 111 222",
                "category_codes": ["PLUMBING"],
                "properties": links,
                **extra,
            },
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def assign(self, issue, provider, user=None, **extra):
        return self.act(
            issue, "assignment/", user or self.lou, {"service_provider_id": provider["id"], **extra}
        )

    def test_reporting_can_name_the_kind_of_problem(self):
        issue = self.reported(category_code="PLUMBING")

        self.assertEqual(issue["category"], {"code": "PLUMBING", "name": "Plumbing"})

    def test_the_kind_of_problem_is_optional_and_must_be_a_listed_one(self):
        self.assertIsNone(self.reported()["category"])
        self.assertEqual(self.report(category_code="NOPE").status_code, 400)

    def test_the_landlord_books_a_provider_and_the_tenant_sees_their_contact_details(self):
        issue = self.reported()
        provider = self.provider()

        response = self.assign(issue, provider, scheduled_at="2026-12-20T09:00:00Z")

        self.assertEqual(response.status_code, 200, response.data)
        seen = self.detail(issue, self.tina).data["assignment"]
        self.assertEqual(seen["provider"]["business_name"], "Smith Plumbing")
        self.assertEqual(seen["provider"]["phone_number"], "0400 111 222")
        self.assertEqual(seen["provider"]["categories"][0]["code"], "PLUMBING")
        self.assertEqual(seen["scheduled_at"].date().isoformat(), "2026-12-20")
        self.assertIsNone(seen["completed_at"])

    def test_the_tenant_is_told_and_the_message_has_no_contact_details(self):
        issue = self.reported()
        self.assign(issue, self.provider())

        (note,) = Notification.objects.filter(
            recipient=self.tina, kind="MAINTENANCE_PROVIDER_ASSIGNED"
        )
        self.assertIn("Smith Plumbing", note.body)
        self.assertNotIn("0400", note.body + note.title)

    def test_contract_notes_never_reach_the_issue(self):
        issue = self.reported()
        self.provider(
            properties=[{"property_id": self.property["id"], "contract_notes": "Net 30 terms"}]
        )
        self.as_user(self.lou)
        providers = self.client.get(PROVIDERS).data["results"]
        self.assign(issue, providers[0])

        self.assertNotIn("Net 30", str(self.detail(issue, self.tina).data))
        self.assertNotIn("Net 30", str(self.detail(issue, self.lou).data))

    def test_only_the_landlord_can_book_and_only_with_their_own_linked_provider(self):
        issue = self.reported()
        mine = self.provider()
        unlinked = self.provider("Elsewhere Ltd", linked=False)
        other_landlord = self.make_user("mia@example.com", "LANDLORD", "Mia", "Cho")
        theirs = self.provider("Mia Electrical", landlord=other_landlord, linked=False)

        self.assertEqual(self.assign(issue, mine, self.tina).status_code, 403)
        self.assertEqual(self.assign(issue, unlinked).status_code, 400)
        self.assertEqual(self.assign(issue, theirs).status_code, 400)
        self.assertIsNone(self.detail(issue, self.lou).data["assignment"])

    def test_booking_again_replaces_the_current_provider_and_keeps_the_old_row(self):
        issue = self.reported()
        first = self.provider("Smith Plumbing")
        second = self.provider("Jones Plumbing")
        self.assign(issue, first)
        self.assign(issue, second)

        seen = self.detail(issue, self.tina).data["assignment"]
        self.assertEqual(seen["provider"]["business_name"], "Jones Plumbing")
        old, new = MaintenanceAssignment.objects.order_by("id")
        self.assertEqual(new.supersedes_assignment_id, old.pk)

    def test_the_landlord_marks_the_visit_done_once(self):
        issue = self.reported()
        self.assertEqual(self.act(issue, "assignment/complete/", self.lou).status_code, 400)
        self.assign(issue, self.provider())

        done = self.act(issue, "assignment/complete/", self.lou)

        self.assertEqual(done.status_code, 200, done.data)
        self.assertIsNotNone(done.data["assignment"]["completed_at"])
        self.assertEqual(self.act(issue, "assignment/complete/", self.lou).status_code, 400)
        self.assertEqual(self.act(issue, "assignment/complete/", self.tina).status_code, 403)

    def test_booking_does_not_change_the_issue_status(self):
        issue = self.reported()

        response = self.assign(issue, self.provider())

        self.assertEqual(response.data["status"], "REPORTED")

    def test_nothing_can_be_booked_on_a_closed_issue(self):
        issue = self.reported()
        provider = self.provider()
        self.propose(issue, self.tina)
        self.answer(issue, self.lou)

        self.assertEqual(self.assign(issue, provider).status_code, 400)

    def test_only_the_landlord_is_offered_options_and_the_actions(self):
        issue = self.reported(category_code="PLUMBING")
        self.provider("Zed Plumbing")
        self.provider("Acme Appliances", category_codes=["APPLIANCES"])

        as_landlord = self.detail(issue, self.lou).data
        as_tenant = self.detail(issue, self.tina).data

        self.assertEqual(
            [row["business_name"] for row in as_landlord["provider_options"]],
            ["Zed Plumbing", "Acme Appliances"],
        )
        self.assertIn("ASSIGN_PROVIDER", as_landlord["actions"])
        self.assertEqual(as_tenant["provider_options"], [])
        self.assertNotIn("ASSIGN_PROVIDER", as_tenant["actions"])

    def test_tenants_and_landlords_can_list_the_kinds_of_problem(self):
        self.as_user(self.tina)

        response = self.client.get(f"{URL}categories/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("PLUMBING", [row["code"] for row in response.data])
