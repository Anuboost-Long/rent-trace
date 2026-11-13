from datetime import date

from tenancies.models import TenancyParty
from tenancies.tests.base import TenancyApiTestCase

PROVIDERS_URL = "/api/landlord/providers/"


class MyPropertyProvidersTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.add_tenant(self.tenancy["id"], self.tina)

    def url(self, tenancy_id=None):
        return f"/api/tenant/tenancies/{tenancy_id or self.tenancy['id']}/providers/"

    def add_provider(self, name, *, linked=True, **link):
        self.as_user(self.lou)
        links = [{"property_id": self.property["id"], **link}] if linked else []
        response = self.post(
            PROVIDERS_URL,
            {
                "business_name": name,
                "phone_number": "0400 111 222",
                "category_codes": ["PLUMBING"],
                "properties": links,
            },
        )
        self.assertEqual(response.status_code, 201, response.data)

    def as_tina(self, tenancy_id=None):
        self.as_user(self.tina)
        return self.client.get(self.url(tenancy_id))

    def test_a_tenant_sees_the_providers_linked_to_their_property_with_contact_details(self):
        self.add_provider("Smith Plumbing", is_recommended=True)

        response = self.as_tina()

        self.assertEqual(response.status_code, 200)
        (row,) = response.data
        self.assertEqual(row["business_name"], "Smith Plumbing")
        self.assertEqual(row["phone_number"], "0400 111 222")
        self.assertTrue(row["is_recommended"])
        self.assertEqual(row["categories"], [{"code": "PLUMBING", "name": "Plumbing"}])

    def test_contract_notes_are_never_sent_to_a_tenant(self):
        self.add_provider("Smith Plumbing", contract_notes="Net 30 terms")

        text = str(self.as_tina().data)

        self.assertNotIn("Net 30", text)
        self.assertNotIn("contract_notes", text)

    def test_preferred_providers_come_first(self):
        self.add_provider("Acme", is_recommended=False)
        self.add_provider("Zed Electrical", is_recommended=True)

        names = [row["business_name"] for row in self.as_tina().data]

        self.assertEqual(names, ["Zed Electrical", "Acme"])

    def test_a_provider_not_linked_to_the_property_is_hidden(self):
        self.add_provider("Elsewhere Ltd", linked=False)

        self.assertEqual(self.as_tina().data, [])

    def test_a_removed_provider_disappears(self):
        self.add_provider("Smith Plumbing")
        self.as_user(self.lou)
        provider_id = self.client.get(PROVIDERS_URL).data["results"][0]["id"]
        self.assertEqual(self.client.delete(f"{PROVIDERS_URL}{provider_id}/").status_code, 204)

        self.assertEqual(self.as_tina().data, [])

    def test_someone_else_cannot_see_the_list(self):
        self.add_provider("Smith Plumbing")
        stranger = self.make_user("sam@example.com", "TENANT", "Sam", "Lee")
        self.as_user(stranger)

        self.assertEqual(self.client.get(self.url()).status_code, 404)

    def test_a_tenant_who_has_left_sees_nothing(self):
        self.add_provider("Smith Plumbing")
        TenancyParty.objects.filter(tenancy_id=self.tenancy["id"]).update(left_at=date(2026, 12, 5))

        self.assertEqual(self.as_tina().data, [])

    def test_landlords_cannot_use_the_tenant_endpoint(self):
        self.as_user(self.lou)

        self.assertEqual(self.client.get(self.url()).status_code, 403)
