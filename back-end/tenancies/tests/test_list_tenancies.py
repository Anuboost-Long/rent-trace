from properties.models import PropertyUnit
from tenancies.models import Tenancy
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TenancyApiTestCase


class ListTenanciesTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.first = self.new_tenancy()
        self.second = self.new_tenancy()
        self.admin_signed_in = False

    def list_as_admin(self, **query):
        if not self.admin_signed_in:
            self.sign_in_as_admin(super_admin=True, email="boss@example.com")
            self.admin_signed_in = True
        return self.client.get(ADMIN_URL, query)

    def test_an_admin_sees_every_tenancy_newest_first(self):
        response = self.list_as_admin()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        ids = [row["id"] for row in response.data["results"]]
        self.assertEqual(ids, [self.second["id"], self.first["id"]])

    def test_a_row_summarises_place_tenants_and_pending_invites(self):
        self.add_tenant(self.first["id"], self.tina)
        self.invite(self.first, email="bob@example.com")

        row = next(r for r in self.list_as_admin().data["results"] if r["id"] == self.first["id"])

        self.assertEqual(row["unit"], {"id": self.unit.pk, "name": "Flat 1"})
        self.assertEqual(row["property"]["id"], self.property["id"])
        self.assertEqual((row["tenant_count"], row["pending_invitations"]), (1, 1))
        self.assertEqual(row["status"], "DRAFT")

    def test_search_finds_a_reference_a_unit_or_a_tenant(self):
        self.add_tenant(self.first["id"], self.tina)
        reference = self.tenancy_row(self.second).reference_no

        for text, expected in (
            (reference, [self.second["id"]]),
            ("tina@example.com", [self.first["id"]]),
            ("Ray", [self.first["id"]]),
            ("flat", [self.second["id"], self.first["id"]]),
            ("nothing-matches", []),
        ):
            with self.subTest(text=text):
                results = self.list_as_admin(q=text).data["results"]
                self.assertEqual([row["id"] for row in results], expected)

    def test_filters_by_status(self):
        Tenancy.objects.filter(pk=self.first["id"]).update(status="ACTIVE")

        results = self.list_as_admin(status="ACTIVE").data["results"]

        self.assertEqual([row["id"] for row in results], [self.first["id"]])
        self.assertEqual(self.list_as_admin(status="NOPE").status_code, 400)

    def test_deleted_tenancies_are_left_out(self):
        Tenancy.objects.filter(pk=self.first["id"]).update(deleted_at="2026-01-01T00:00:00Z")

        self.assertEqual(self.list_as_admin().data["count"], 1)

    def test_a_landlord_sees_only_tenancies_on_their_own_properties(self):
        other_property = self.new_property(self.amy)
        other_unit = PropertyUnit.objects.create(
            property_id=other_property["id"], name="Flat 9", unit_type="APARTMENT"
        )
        self.as_user(self.amy)
        self.post(LANDLORD_URL, {"property_unit_id": other_unit.pk, "start_date": "2026-12-01"})

        self.as_user(self.lou)
        response = self.client.get(LANDLORD_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_a_viewer_without_the_permission_is_refused(self):
        self.make_role("NOVIEW", ["bans.view"])
        self.sign_in_as_admin(roles=("NOVIEW",), email="nope@example.com")

        self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
