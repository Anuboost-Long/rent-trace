from providers.models import PropertyServiceProvider
from providers.tests.base import URL, ProvidersApiTestCase


class UpdateProviderTests(ProvidersApiTestCase):
    def patch(self, provider, changes):
        return self.client.patch(f"{URL}{provider['id']}/", changes, format="json")

    def test_changes_details_and_leaves_the_rest(self):
        made = self.new_provider(category_codes=["PLUMBING"])

        response = self.patch(made, {"business_name": "Smith and Sons", "contact_name": "Sam"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["business_name"], "Smith and Sons")
        self.assertEqual(response.data["phone_number"], "0400 111 222")
        self.assertEqual([c["code"] for c in response.data["categories"]], ["PLUMBING"])

    def test_cannot_remove_the_last_way_to_reach_the_provider(self):
        made = self.new_provider()

        response = self.patch(made, {"phone_number": ""})

        self.assertEqual(response.status_code, 400)

    def test_can_swap_one_contact_method_for_another(self):
        made = self.new_provider()

        response = self.patch(made, {"phone_number": "", "email": "sam@example.com"})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["phone_number"])

    def test_replaces_the_category_set(self):
        made = self.new_provider(category_codes=["PLUMBING", "PESTS"])

        response = self.patch(made, {"category_codes": ["PESTS", "GENERAL"]})

        codes = [c["code"] for c in response.data["categories"]]
        self.assertEqual(sorted(codes), ["GENERAL", "PESTS"])

    def test_unlinking_then_relinking_a_property_works(self):
        home = self.new_property(self.lou)
        made = self.new_provider(properties=[self.link(home["id"])])

        gone = self.patch(made, {"properties": []})
        again = self.patch(made, {"properties": [self.link(home["id"], is_recommended=True)]})

        self.assertEqual(gone.data["properties"], [])
        (linked,) = again.data["properties"]
        self.assertTrue(linked["is_recommended"])
        self.assertEqual(PropertyServiceProvider.objects.count(), 2)
        self.assertEqual(PropertyServiceProvider.objects.filter(deleted_at__isnull=True).count(), 1)

    def test_changes_a_link_without_adding_another(self):
        home = self.new_property(self.lou)
        made = self.new_provider(properties=[self.link(home["id"])])

        response = self.patch(
            made, {"properties": [self.link(home["id"], contract_notes="Annual contract")]}
        )

        self.assertEqual(response.data["properties"][0]["contract_notes"], "Annual contract")
        self.assertEqual(PropertyServiceProvider.objects.count(), 1)

    def test_a_property_you_do_not_own_cannot_be_linked(self):
        theirs = self.new_property(self.amy)
        made = self.new_provider(self.lou)
        self.as_user(self.lou)

        response = self.patch(made, {"properties": [self.link(theirs["id"])]})

        self.assertEqual(response.status_code, 400)

    def test_another_landlords_provider_is_not_found(self):
        made = self.new_provider(self.lou)
        self.as_user(self.amy)

        response = self.patch(made, {"business_name": "Mine now"})

        self.assertEqual(response.status_code, 404)
