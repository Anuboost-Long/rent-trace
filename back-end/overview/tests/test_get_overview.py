from datetime import timedelta

from django.utils import timezone

from accounts.models import AccountAccessHistory, Ban
from properties.models import PropertyUnit
from tenancies.models import Tenancy, TenancyInvitation
from tenancies.tests.base import TenancyApiTestCase

URL = "/api/overview/"


class OverviewTests(TenancyApiTestCase):
    def sign_in_boss(self):
        self.admin = self.sign_in_as_admin(super_admin=True, email="boss@example.com")

    def test_counts_people_properties_tenancies_and_bans(self):
        first = self.new_tenancy()
        self.new_tenancy()
        Tenancy.objects.filter(pk=first["id"]).update(status="ACTIVE")
        self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        Ban.objects.create(ban_type="EMAIL", value="spam@example.com", reason="Spam")
        Ban.objects.create(
            ban_type="EMAIL",
            value="old@example.com",
            reason="Old",
            lifted_at=timezone.now(),
            lifted_by=self.lou,
            lift_reason="Fine",
        )
        self.sign_in_boss()

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["properties"], {"properties": 1, "units": 1})
        self.assertEqual(data["tenancies"]["by_status"]["ACTIVE"], 1)
        self.assertEqual(data["tenancies"]["by_status"]["DRAFT"], 1)
        self.assertEqual(data["tenancies"]["by_status"]["ENDED"], 0)
        self.assertEqual(data["active_bans"], 1)
        self.assertEqual(data["people"]["suspended"], 0)
        self.assertGreaterEqual(data["people"]["users"], 4)

    def test_tenancies_ending_within_sixty_days_are_counted_once_active(self):
        soon = self.new_tenancy()
        later = self.new_tenancy()
        draft = self.new_tenancy()
        today = timezone.now().date()
        started = today - timedelta(days=200)
        Tenancy.objects.filter(pk=soon["id"]).update(
            status="ACTIVE", start_date=started, end_date=today + timedelta(days=30)
        )
        Tenancy.objects.filter(pk=later["id"]).update(
            status="ACTIVE", start_date=started, end_date=today + timedelta(days=90)
        )
        Tenancy.objects.filter(pk=draft["id"]).update(
            start_date=started, end_date=today + timedelta(days=10)
        )
        self.sign_in_boss()

        self.assertEqual(self.client.get(URL).data["tenancies"]["ending_soon"], 1)

    def test_counts_pending_and_expired_invitations_but_not_revoked_ones(self):
        tenancy = self.new_tenancy()
        for email in ("a@example.com", "b@example.com", "c@example.com"):
            self.invite(tenancy, email=email)
        invites = TenancyInvitation.objects.order_by("id")
        invites.filter(email_normalized="b@example.com").update(
            created_at=timezone.now() - timedelta(days=8),
            expires_at=timezone.now() - timedelta(days=1),
        )
        invites.filter(email_normalized="c@example.com").update(revoked_at=timezone.now())
        self.sign_in_boss()

        figures = self.client.get(URL).data["tenancies"]

        self.assertEqual((figures["pending_invitations"], figures["expired_invitations"]), (1, 1))

    def test_recent_activity_lists_account_changes_newest_first(self):
        self.sign_in_boss()
        for action in ("FIRST", "SECOND"):
            AccountAccessHistory.objects.create(
                user=self.lou,
                action=action,
                before_values={},
                after_values={},
                reason="Test",
                correlation_id="00000000-0000-0000-0000-000000000000",
                created_by=self.admin,
            )

        activity = self.client.get(URL).data["activity"]

        self.assertEqual([entry["action"] for entry in activity[:2]], ["SECOND", "FIRST"])
        self.assertEqual(activity[0]["person"]["id"], self.lou.pk)
        self.assertEqual(activity[0]["by"]["id"], self.admin.pk)

    def test_blocks_the_person_cannot_see_are_null(self):
        self.make_role("BANNER", ["bans.view"])
        self.sign_in_as_admin(roles=("BANNER",), email="banner@example.com")

        data = self.client.get(URL).data

        self.assertEqual(
            (data["people"], data["properties"], data["tenancies"], data["activity"]),
            (None, None, None, None),
        )
        self.assertEqual(data["active_bans"], 0)

    def test_deleted_properties_and_units_are_not_counted(self):
        PropertyUnit.objects.filter(pk=self.unit.pk).update(deleted_at=timezone.now())
        self.sign_in_boss()

        self.assertEqual(self.client.get(URL).data["properties"], {"properties": 1, "units": 0})

    def test_landlords_and_tenants_are_refused(self):
        self.as_user(self.lou)
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.as_user(self.tina)
        self.assertEqual(self.client.get(URL).status_code, 403)

    def test_needs_sign_in(self):
        self.client.credentials()
        self.assertEqual(self.client.get(URL).status_code, 401)


class LandlordOverviewTests(TenancyApiTestCase):
    URL = "/api/landlord/overview/"

    def test_a_landlord_sees_figures_for_their_own_properties_only(self):
        mine = self.new_tenancy()
        self.invite(mine)
        amy_place = self.new_property(self.amy)
        amy_unit = PropertyUnit.objects.create(
            property_id=amy_place["id"], name="Flat 9", unit_type="APARTMENT"
        )
        self.as_user(self.amy)
        self.post(
            "/api/landlord/tenancies/",
            {"property_unit_id": amy_unit.pk, "start_date": "2026-12-01"},
        )
        self.as_user(self.lou)

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["properties"], {"properties": 1, "units": 1})
        self.assertEqual(response.data["tenancies"]["by_status"]["DRAFT"], 1)
        self.assertEqual(response.data["tenancies"]["pending_invitations"], 1)
        self.assertIsNone(response.data["people"])
        self.assertIsNone(response.data["active_bans"])
        self.assertIsNone(response.data["activity"])

    def test_admins_and_tenants_cannot_use_it(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.assertEqual(self.client.get(self.URL).status_code, 403)
        self.as_user(self.tina)
        self.assertEqual(self.client.get(self.URL).status_code, 403)
