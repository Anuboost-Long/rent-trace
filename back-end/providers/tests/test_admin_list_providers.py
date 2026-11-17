from accounts.models import RolePermissionBridge
from providers.tests.base import ProvidersApiTestCase

ADMIN_URL = "/api/admin/providers/"


class AdminListProvidersTests(ProvidersApiTestCase):
    def sign_in_boss(self):
        return self.sign_in_as_admin(super_admin=True, email="boss@example.com")

    def test_an_admin_sees_every_landlords_providers_with_the_owner(self):
        self.new_provider(self.lou, business_name="Zed Electrical")
        self.new_provider(self.amy, business_name="Amy's Locksmith")
        self.sign_in_boss()

        response = self.client.get(ADMIN_URL)

        self.assertEqual(response.status_code, 200)
        rows = {row["business_name"]: row for row in response.data["results"]}
        self.assertEqual(set(rows), {"Zed Electrical", "Amy's Locksmith"})
        self.assertEqual(rows["Zed Electrical"]["owner"]["first_name"], "Lou")
        self.assertEqual(rows["Amy's Locksmith"]["owner"]["first_name"], "Amy")

    def test_the_list_filters_by_words_and_by_trade(self):
        self.new_provider(self.lou, business_name="Acme Plumbing", category_codes=["PLUMBING"])
        self.new_provider(
            self.amy,
            business_name="Zed Electrical",
            contact_name="Pat",
            category_codes=["ELECTRICAL"],
        )
        self.sign_in_boss()

        by_name = self.client.get(ADMIN_URL, {"q": "acme"}).data["results"]
        by_contact = self.client.get(ADMIN_URL, {"q": "pat"}).data["results"]
        by_trade = self.client.get(ADMIN_URL, {"category": "ELECTRICAL"}).data["results"]

        self.assertEqual([row["business_name"] for row in by_name], ["Acme Plumbing"])
        self.assertEqual([row["business_name"] for row in by_contact], ["Zed Electrical"])
        self.assertEqual([row["business_name"] for row in by_trade], ["Zed Electrical"])

    def test_linked_properties_are_shown_but_contract_notes_are_not(self):
        home = self.new_property(self.lou)
        self.new_provider(self.lou, properties=[self.link(home["id"], contract_notes="Annual")])
        self.sign_in_boss()

        row = self.client.get(ADMIN_URL).data["results"][0]

        self.assertEqual(len(row["properties"]), 1)
        self.assertEqual(
            set(row["properties"][0]), {"property_id", "property_name", "is_recommended"}
        )

    def test_deleted_providers_are_not_listed(self):
        made = self.new_provider(self.lou)
        self.as_user(self.lou)
        self.client.delete(f"/api/landlord/providers/{made['id']}/")
        self.sign_in_boss()

        self.assertEqual(self.client.get(ADMIN_URL).data["results"], [])

    def test_an_admin_can_list_the_trades(self):
        self.sign_in_boss()

        response = self.client.get(f"{ADMIN_URL}categories/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("PLUMBING", [row["code"] for row in response.data])

    def test_landlords_and_tenants_are_refused(self):
        tina = self.make_user("tina@example.com", "TENANT", "Tina", "Ray")
        for user in (self.lou, tina):
            self.as_user(user)
            self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
            self.assertEqual(self.client.get(f"{ADMIN_URL}categories/").status_code, 403)

    def test_an_admin_without_the_permission_is_refused(self):
        RolePermissionBridge.objects.filter(permission__code="providers.admin_view").delete()
        self.sign_in_as_admin(email="plain@example.com")

        self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
