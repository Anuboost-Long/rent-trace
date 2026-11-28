from maintenance.models import MaintenanceIssue
from maintenance.tests.base import MaintenanceApiTestCase
from maintenance.tests.test_assign_provider import PROVIDERS
from providers.models import MaintenanceAssignment

ADMIN_URL = "/api/admin/maintenance/"


class AdminPartyActionTests(MaintenanceApiTestCase):
    def setUp(self):
        super().setUp()
        self.issue = self.reported()

    def admin_post(self, path, data=None, *, boss=None):
        if boss is None:
            self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        return self.post(f"{ADMIN_URL}{self.issue['id']}/{path}", data or {})

    def last_history(self):
        return (
            MaintenanceIssue.objects.get(pk=self.issue["id"])
            .status_history.order_by("sequence_no")
            .last()
        )

    def test_a_super_admin_proposes_a_closing_and_the_tenant_can_answer_it(self):
        response = self.admin_post(
            "closure/", {"outcome": "FIXED", "reason": "Landlord confirmed."}
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["open_closure"]["proposer_side"], "LANDLORD")
        approved = self.answer(self.issue, self.tina)
        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertEqual(approved.data["status"], "CLOSED")

    def test_a_super_admin_can_take_back_their_own_proposal(self):
        self.admin_post("closure/", {"outcome": "FIXED", "reason": "Done."})

        response = self.admin_post("closure/withdraw/", boss=True)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertIsNone(response.data["open_closure"])

    def test_a_super_admin_approves_for_the_landlord_and_the_history_says_so(self):
        self.propose(self.issue, self.tina)
        proposal = self.detail(self.issue, self.tina).data["open_closure"]
        boss = self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        response = self.post(f"{ADMIN_URL}{self.issue['id']}/closure/{proposal['id']}/approve/")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "CLOSED")
        row = self.last_history()
        self.assertEqual((row.actor, row.on_behalf_of), (boss, self.lou))

    def test_a_super_admin_rejects_for_the_tenants_a_landlord_proposal(self):
        self.propose(self.issue, self.lou)
        proposal = self.detail(self.issue, self.lou).data["open_closure"]
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        response = self.post(f"{ADMIN_URL}{self.issue['id']}/closure/{proposal['id']}/reject/")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertIsNone(response.data["open_closure"])
        self.assertNotEqual(response.data["status"], "CLOSED")

    def test_an_admin_cannot_answer_a_proposal_they_made(self):
        self.admin_post("closure/", {"outcome": "FIXED", "reason": "Done."})
        proposal = MaintenanceIssue.objects.get().open_closure_proposal

        response = self.admin_post(f"closure/{proposal.pk}/approve/", boss=True)

        self.assertEqual(response.status_code, 403)

    def test_an_admin_who_is_not_a_super_admin_cannot_act_for_a_party(self):
        self.sign_in_as_admin(email="plain@example.com")

        response = self.post(
            f"{ADMIN_URL}{self.issue['id']}/closure/", {"outcome": "FIXED", "reason": "Done."}
        )

        self.assertEqual(response.status_code, 403)

    def test_a_super_admin_books_one_of_the_landlords_tradespeople_and_marks_the_visit_done(self):
        self.as_user(self.lou)
        created = self.post(
            PROVIDERS,
            {
                "business_name": "Smith Plumbing",
                "phone_number": "0400 111 222",
                "category_codes": ["PLUMBING"],
                "properties": [{"property_id": self.property["id"], "is_recommended": False}],
            },
        )
        self.assertEqual(created.status_code, 201, created.data)

        booked = self.admin_post("assignment/", {"service_provider_id": created.data["id"]})
        done = self.admin_post("assignment/complete/", boss=True)

        self.assertEqual(booked.status_code, 200, booked.data)
        self.assertEqual(done.status_code, 200, done.data)
        self.assertIsNotNone(MaintenanceAssignment.objects.get().completed_at)

    def test_booking_a_tradesperson_the_landlord_has_not_linked_is_refused(self):
        response = self.admin_post("assignment/", {"service_provider_id": 999999})

        self.assertEqual(response.status_code, 400)

    def test_marking_a_visit_done_before_booking_is_refused(self):
        response = self.admin_post("assignment/complete/")

        self.assertEqual(response.status_code, 400)


class AdminIssueDetailTests(MaintenanceApiTestCase):
    def test_the_admin_sees_the_owners_tradespeople_to_book(self):
        issue = self.reported()
        self.as_user(self.lou)
        created = self.post(
            PROVIDERS,
            {
                "business_name": "Smith Plumbing",
                "phone_number": "0400 111 222",
                "category_codes": ["PLUMBING"],
                "properties": [{"property_id": self.property["id"], "is_recommended": True}],
            },
        )
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        detail = self.client.get(f"{ADMIN_URL}{issue['id']}/")

        self.assertEqual(
            [option["business_name"] for option in detail.data["provider_options"]],
            ["Smith Plumbing"],
        )
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(detail.data["tenancy_id"], self.tenancy["id"])

    def test_a_proposal_the_admin_made_can_only_be_withdrawn_by_them(self):
        issue = self.reported()
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.post(
            f"{ADMIN_URL}{issue['id']}/closure/",
            {"outcome": "FIXED", "reason": "Landlord says done."},
        )

        detail = self.client.get(f"{ADMIN_URL}{issue['id']}/")

        self.assertEqual(detail.data["actions"], ["WITHDRAW_CLOSURE"])
