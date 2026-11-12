from datetime import date, timedelta

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from tenancies.models import Tenancy, TenancyParty
from tenancies.tests.base import TenancyApiTestCase

URL = "/api/tenant/tenancies/"


class MyTenanciesTests(TenancyApiTestCase):
    def as_tina(self):
        self.as_user(self.tina)
        return self.client.get(URL)

    def test_lists_my_tenancies_with_place_unit_and_landlord_name(self):
        mine = self.new_tenancy()
        self.add_tenant(mine["id"], self.tina, is_primary=True)

        response = self.as_tina()

        self.assertEqual(response.status_code, 200)
        (row,) = response.data
        self.assertEqual(row["id"], mine["id"])
        self.assertEqual(
            row["unit"],
            {"id": self.unit.pk, "name": "Flat 1", "unit_type": "APARTMENT", "description": None},
        )
        self.assertEqual(row["property"]["id"], self.property["id"])
        self.assertIn("address_line_1", row["property"])
        self.assertIn("postcode", row["property"])
        self.assertEqual(row["landlord"], "Lou Reed")
        self.assertEqual(
            (row["status"], row["is_primary"], row["is_current"]), ("DRAFT", True, True)
        )
        self.assertEqual(row["left_at"], None)

    def test_the_landlords_email_and_phone_are_never_included(self):
        self.add_tenant(self.new_tenancy()["id"], self.tina)

        text = str(self.as_tina().data)

        self.assertNotIn("lou@example.com", text)
        self.assertNotIn("phone", text)

    def test_only_tenancies_i_joined_are_listed(self):
        mine = self.new_tenancy()
        other = self.new_tenancy()
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        self.add_tenant(mine["id"], self.tina)
        self.add_tenant(other["id"], sam)

        self.assertEqual([row["id"] for row in self.as_tina().data], [mine["id"]])

    def test_ended_cancelled_and_left_tenancies_are_history_not_current(self):
        ended, cancelled, left, current = (self.new_tenancy() for _ in range(4))
        for tenancy in (ended, cancelled, left, current):
            self.add_tenant(tenancy["id"], self.tina)
        Tenancy.objects.filter(pk=ended["id"]).update(status="ENDED")
        Tenancy.objects.filter(pk=cancelled["id"]).update(status="CANCELLED")
        TenancyParty.objects.filter(tenancy_id=left["id"]).update(left_at=date(2026, 12, 20))

        by_id = {row["id"]: row for row in self.as_tina().data}

        self.assertEqual(len(by_id), 4)
        self.assertEqual(
            [by_id[t["id"]]["is_current"] for t in (ended, cancelled, left, current)],
            [False, False, False, True],
        )
        self.assertEqual(by_id[left["id"]]["left_at"], "2026-12-20")

    def test_newest_start_first(self):
        older, newer = self.new_tenancy(), self.new_tenancy()
        Tenancy.objects.filter(pk=older["id"]).update(start_date=date(2026, 1, 1))
        Tenancy.objects.filter(pk=newer["id"]).update(start_date=date(2026, 6, 1))
        for tenancy in (older, newer):
            self.add_tenant(tenancy["id"], self.tina)

        self.assertEqual([row["id"] for row in self.as_tina().data], [newer["id"], older["id"]])

    def test_rent_and_bond_show_when_set(self):
        mine = self.new_tenancy()
        self.add_tenant(mine["id"], self.tina)
        Tenancy.objects.filter(pk=mine["id"]).update(
            rent_amount="450.00", rent_frequency="WEEKLY", bond_amount="1800.00"
        )

        row = self.as_tina().data[0]

        self.assertEqual(
            (row["rent_amount"], row["rent_frequency"], row["bond_amount"], row["currency"]),
            ("450.00", "WEEKLY", "1800.00", "AUD"),
        )

    def test_the_list_costs_the_same_number_of_queries_however_many_tenancies(self):
        self.add_tenant(self.new_tenancy()["id"], self.tina)
        with CaptureQueriesContext(connection) as one:
            self.as_tina()
        for _ in range(3):
            self.add_tenant(self.new_tenancy()["id"], self.tina)

        with CaptureQueriesContext(connection) as several:
            response = self.as_tina()

        self.assertEqual(len(response.data), 4)
        self.assertEqual(len(several), len(one))

    def test_deleted_tenancies_are_left_out(self):
        mine = self.new_tenancy()
        self.add_tenant(mine["id"], self.tina)
        Tenancy.objects.filter(pk=mine["id"]).update(deleted_at=timezone.now() - timedelta(days=1))

        self.assertEqual(self.as_tina().data, [])

    def test_detail_names_the_other_current_tenants_only(self):
        mine = self.new_tenancy()
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        gone = self.make_user("gus@example.com", "TENANT", "Gus", "Hill")
        self.add_tenant(mine["id"], self.tina)
        self.add_tenant(mine["id"], sam, is_primary=True)
        self.add_tenant(mine["id"], gone)
        TenancyParty.objects.filter(tenant=gone).update(left_at=date(2026, 12, 2))
        self.as_user(self.tina)

        response = self.client.get(f"{URL}{mine['id']}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["housemates"],
            [{"first_name": "Sam", "last_name": "Fox", "is_primary": True}],
        )
        self.assertNotIn("sam@example.com", str(response.data))

    def test_someone_elses_tenancy_is_not_found(self):
        other = self.new_tenancy()
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        self.add_tenant(other["id"], sam)
        self.as_user(self.tina)

        self.assertEqual(self.client.get(f"{URL}{other['id']}/").status_code, 404)

    def test_landlords_admins_and_signed_out_visitors_are_refused(self):
        self.as_user(self.lou)
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.get(URL).status_code, 401)
