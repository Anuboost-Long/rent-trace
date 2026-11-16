from accounts.models import RolePermissionBridge
from maintenance.tests.base import MaintenanceApiTestCase
from properties.models import PropertyUnit
from tenancies.models import Tenancy

ADMIN_URL = "/api/admin/maintenance/"


class AdminIssuesTests(MaintenanceApiTestCase):
    def sign_in_boss(self):
        return self.sign_in_as_admin(super_admin=True, email="boss@example.com")

    def issue_on_another_landlords_property(self):
        place = self.new_property(self.amy, address_line_1="9 Other Rd", suburb="Carlton")
        unit = PropertyUnit.objects.create(
            property_id=place["id"], name="Flat 9", unit_type="APARTMENT"
        )
        tenancy = self.new_tenancy(self.amy, property_unit_id=unit.pk)
        Tenancy.objects.filter(pk=tenancy["id"]).update(status="ACTIVE")
        self.add_tenant(tenancy["id"], self.sam)
        return self.reported(user=self.sam, tenancy=tenancy, title="Heater is broken")

    def test_an_admin_sees_issues_from_every_landlord(self):
        mine = self.reported()
        theirs = self.issue_on_another_landlords_property()
        self.sign_in_boss()

        response = self.client.get(ADMIN_URL)

        self.assertEqual(response.status_code, 200)
        ids = {row["id"] for row in response.data["results"]}
        self.assertEqual(ids, {mine["id"], theirs["id"]})

    def test_the_list_filters_by_status_and_searches_title_and_suburb(self):
        self.reported()
        theirs = self.issue_on_another_landlords_property()
        self.sign_in_boss()

        by_title = self.client.get(ADMIN_URL, {"q": "heater"}).data["results"]
        by_suburb = self.client.get(ADMIN_URL, {"q": "carlton"}).data["results"]
        closed = self.client.get(ADMIN_URL, {"status": "CLOSED"}).data["results"]

        self.assertEqual([row["id"] for row in by_title], [theirs["id"]])
        self.assertEqual([row["id"] for row in by_suburb], [theirs["id"]])
        self.assertEqual(closed, [])

    def test_the_detail_offers_an_admin_no_actions(self):
        issue = self.reported()
        self.sign_in_boss()

        response = self.client.get(f"{ADMIN_URL}{issue['id']}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Kitchen tap drips")
        self.assertEqual(response.data["actions"], [])
        self.assertIsNone(response.data["my_side"])
        self.assertEqual(response.data["provider_options"], [])

    def test_an_unknown_issue_is_not_found(self):
        self.sign_in_boss()
        self.assertEqual(self.client.get(f"{ADMIN_URL}999999/").status_code, 404)

    def test_landlords_and_tenants_are_refused(self):
        issue = self.reported()
        for user in (self.lou, self.tina):
            self.as_user(user)
            self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
            self.assertEqual(self.client.get(f"{ADMIN_URL}{issue['id']}/").status_code, 403)

    def test_an_admin_without_the_permission_is_refused(self):
        RolePermissionBridge.objects.filter(permission__code="maintenance.admin_view").delete()
        self.sign_in_as_admin(email="plain@example.com")

        self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
