from datetime import timedelta

from django.utils import timezone

from notifications.models import Notification
from tenancies.models import Tenancy, TenancyParty
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TenancyApiTestCase


class TenancyLifecycleTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.today = timezone.now().date()
        self.tenancy = self.new_tenancy()

    def act(self, action, tenancy=None, url=LANDLORD_URL, user=None):
        self.as_user(user or self.lou)
        return self.post(f"{url}{(tenancy or self.tenancy)['id']}/{action}/")

    def row(self, tenancy=None):
        return Tenancy.objects.get(pk=(tenancy or self.tenancy)["id"])

    def join(self, tenancy=None, user=None, days_ago=30):
        party = self.add_tenant((tenancy or self.tenancy)["id"], user or self.tina)
        TenancyParty.objects.filter(pk=party.pk).update(
            joined_at=self.today - timedelta(days=days_ago)
        )
        return party

    def start_in_past(self, tenancy=None, days_ago=20, end_date=None):
        Tenancy.objects.filter(pk=(tenancy or self.tenancy)["id"]).update(
            start_date=self.today - timedelta(days=days_ago), end_date=end_date
        )

    def kinds_for(self, person):
        return [row.kind for row in Notification.objects.filter(recipient=person).order_by("id")]

    def test_a_landlord_starts_a_tenancy_that_has_a_tenant(self):
        self.join()

        response = self.act("activate")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "ACTIVE")
        self.assertEqual(self.row().updated_by, self.lou)
        self.assertEqual(self.kinds_for(self.tina), ["TENANCY_STARTED"])

    def test_a_tenancy_with_no_tenant_cannot_start(self):
        response = self.act("activate")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.row().status, "DRAFT")

    def test_only_a_draft_can_start(self):
        self.join()
        self.act("activate")

        self.assertEqual(self.act("activate").status_code, 400)

    def test_a_unit_cannot_have_two_overlapping_active_tenancies(self):
        first = self.tenancy
        second = self.new_tenancy(start_date="2026-12-15")
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        self.join(first)
        self.join(second, sam)
        self.assertEqual(self.act("activate", first).status_code, 200)

        blocked = self.act("activate", second)

        self.assertEqual(blocked.status_code, 400)
        self.assertEqual(self.row(second).status, "DRAFT")

    def test_back_to_back_tenancies_on_one_unit_are_allowed(self):
        first = self.new_tenancy(start_date="2026-12-01", end_date="2027-01-01")
        second = self.new_tenancy(start_date="2027-01-01")
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        self.join(first)
        self.join(second, sam)
        self.act("activate", first)

        self.assertEqual(self.act("activate", second).status_code, 200)

    def test_ending_sets_the_end_date_today_and_releases_the_tenants(self):
        self.join()
        self.act("activate")
        self.start_in_past()

        response = self.act("end")

        self.assertEqual(response.status_code, 200, response.data)
        saved = self.row()
        self.assertEqual((saved.status, saved.end_date), ("ENDED", self.today))
        self.assertEqual(TenancyParty.objects.get().left_at, self.today)
        self.assertEqual(self.kinds_for(self.tina), ["TENANCY_STARTED", "TENANCY_ENDED"])

    def test_starting_a_tenancy_marks_the_unit_occupied_and_ending_frees_it(self):
        self.join()

        self.act("activate")
        self.unit.refresh_from_db()
        self.assertEqual(self.unit.occupancy_status, "OCCUPIED")

        self.start_in_past()
        self.act("end")
        self.unit.refresh_from_db()
        self.assertEqual(self.unit.occupancy_status, "VACANT")

    def test_an_unavailable_unit_stays_unavailable(self):
        self.join()
        self.unit.occupancy_status = "UNAVAILABLE"
        self.unit.save()

        self.act("activate")

        self.unit.refresh_from_db()
        self.assertEqual(self.unit.occupancy_status, "UNAVAILABLE")

    def test_ending_keeps_an_end_date_already_in_the_past(self):
        self.join()
        self.act("activate")
        past_end = self.today - timedelta(days=3)
        self.start_in_past(end_date=past_end)

        self.act("end")

        self.assertEqual(self.row().end_date, past_end)

    def test_a_tenant_who_joined_today_leaves_tomorrow(self):
        self.join(days_ago=0)
        self.act("activate")
        self.start_in_past()

        self.assertEqual(self.act("end").status_code, 200)

        self.assertEqual(TenancyParty.objects.get().left_at, self.today + timedelta(days=1))

    def test_a_tenancy_that_has_not_started_cannot_be_ended(self):
        self.join()
        self.act("activate")

        response = self.act("end")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Cancel", str(response.data))
        self.assertEqual(self.row().status, "ACTIVE")

    def test_only_an_active_tenancy_can_be_ended(self):
        self.assertEqual(self.act("end").status_code, 400)

    def test_cancelling_a_draft_releases_anyone_who_joined(self):
        self.join()

        response = self.act("cancel")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.row().status, "CANCELLED")
        self.assertIsNotNone(TenancyParty.objects.get().left_at)
        self.assertEqual(self.kinds_for(self.tina), ["TENANCY_CANCELLED"])

    def test_an_active_or_closed_tenancy_cannot_be_cancelled(self):
        self.join()
        self.act("activate")
        self.assertEqual(self.act("cancel").status_code, 400)

        other = self.new_tenancy()
        self.act("cancel", other)
        self.assertEqual(self.act("cancel", other).status_code, 400)

    def test_nothing_in_the_notifications_carries_contact_details(self):
        self.join()
        self.act("activate")

        text = " ".join(
            row.title + row.body for row in Notification.objects.filter(recipient=self.tina)
        )

        self.assertNotIn("@", text)
        self.assertNotIn("lou", text.lower())

    def test_an_ended_tenancy_takes_no_new_invitations_or_joiners(self):
        self.join()
        self.act("activate")
        self.start_in_past()
        self.act("end")

        self.assertEqual(self.invite(self.tenancy, email="new@example.com").status_code, 400)

    def test_another_landlords_tenancy_is_not_found(self):
        for action in ("activate", "end", "cancel"):
            with self.subTest(action=action):
                self.assertEqual(self.act(action, user=self.amy).status_code, 404)
        self.assertEqual(self.row().status, "DRAFT")

    def test_tenants_are_refused(self):
        for action in ("activate", "end", "cancel"):
            with self.subTest(action=action):
                self.assertEqual(self.act(action, user=self.tina).status_code, 403)

    def test_an_admin_can_do_all_three_on_any_tenancy(self):
        other = self.new_tenancy()
        self.join()
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        started = self.post(f"{ADMIN_URL}{self.tenancy['id']}/activate/")
        self.start_in_past()
        ended = self.post(f"{ADMIN_URL}{self.tenancy['id']}/end/")
        cancelled = self.post(f"{ADMIN_URL}{other['id']}/cancel/")

        self.assertEqual(
            [started.status_code, ended.status_code, cancelled.status_code], [200, 200, 200]
        )
