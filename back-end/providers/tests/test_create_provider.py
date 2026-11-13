from providers.models import ServiceProvider
from providers.tests.base import URL, ProvidersApiTestCase


class CreateProviderTests(ProvidersApiTestCase):
    def test_landlord_adds_a_provider_with_categories_and_properties(self):
        home = self.new_property(self.lou)

        created = self.new_provider(
            contact_name="Sam Smith",
            category_codes=["PLUMBING", "HEATING_COOLING"],
            properties=[self.link(home["id"], is_recommended=True, contract_notes="Net 30")],
        )

        self.assertEqual(created["business_name"], "Smith Plumbing")
        self.assertEqual(
            [c["code"] for c in created["categories"]], ["HEATING_COOLING", "PLUMBING"]
        )
        (linked,) = created["properties"]
        self.assertEqual(linked["property_id"], home["id"])
        self.assertTrue(linked["is_recommended"])
        self.assertEqual(linked["contract_notes"], "Net 30")
        self.assertEqual(ServiceProvider.objects.get().owner, self.lou)

    def test_needs_a_way_to_reach_the_provider(self):
        self.as_user(self.lou)

        response = self.post(URL, {"business_name": "Smith Plumbing"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_number", response.data)

    def test_blank_contact_fields_do_not_count_as_a_way_to_reach_them(self):
        self.as_user(self.lou)

        response = self.post(
            URL, {"business_name": "Smith Plumbing", "phone_number": "", "email": "", "website": ""}
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(ServiceProvider.objects.exists())

    def test_blank_optional_text_is_stored_as_nothing(self):
        self.new_provider(contact_name="", description="")

        stored = ServiceProvider.objects.get()
        self.assertIsNone(stored.contact_name)
        self.assertIsNone(stored.description)

    def test_unknown_categories_are_rejected(self):
        self.as_user(self.lou)

        response = self.post(URL, self.details(category_codes=["PLUMBING", "ROOFING"]))

        self.assertEqual(response.status_code, 400)
        self.assertIn("ROOFING", str(response.data["category_codes"]))

    def test_a_property_you_do_not_own_cannot_be_linked(self):
        theirs = self.new_property(self.amy)
        self.as_user(self.lou)

        response = self.post(URL, self.details(properties=[self.link(theirs["id"])]))

        self.assertEqual(response.status_code, 400)
        self.assertIn("properties", response.data)
        self.assertFalse(ServiceProvider.objects.exists())

    def test_a_tenant_cannot_add_a_provider(self):
        self.as_user(self.tina)

        response = self.post(URL, self.details())

        self.assertEqual(response.status_code, 403)

    def setUp(self):
        super().setUp()
        self.tina = self.make_user("tina@example.com", "TENANT", "Tina", "Ray")
