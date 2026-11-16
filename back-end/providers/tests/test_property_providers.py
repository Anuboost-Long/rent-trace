from providers.models import PropertyServiceProvider
from providers.tests.base import ProvidersApiTestCase


class PropertyProvidersTests(ProvidersApiTestCase):
    def setUp(self):
        super().setUp()
        self.first = self.new_property(self.lou, address_line_1="1 First St")
        self.second = self.new_property(self.lou, address_line_1="2 Second St")
        self.plumber = self.new_provider(self.lou, business_name="Acme Plumbing")
        self.sparky = self.new_provider(self.lou, business_name="Zed Electrical")
        self.as_user(self.lou)

    def url(self, place, *more):
        return "/".join(["/api/landlord/properties", str(place["id"]), "providers", *more]) + "/"

    def link(self, place, *providers):
        self.as_user(self.lou)
        return self.post(
            self.url(place), {"provider_ids": [provider["id"] for provider in providers]}
        )

    def names(self, response):
        return [row["business_name"] for row in response.data]

    def test_several_saved_contacts_are_linked_in_one_step(self):
        response = self.link(self.second, self.plumber, self.sparky)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.names(response), ["Acme Plumbing", "Zed Electrical"])
        self.assertEqual(self.names(self.client.get(self.url(self.first))), [])

    def test_linking_again_skips_contacts_already_linked(self):
        self.link(self.second, self.plumber)

        response = self.link(self.second, self.plumber, self.sparky)

        self.assertEqual(self.names(response), ["Acme Plumbing", "Zed Electrical"])
        self.assertEqual(PropertyServiceProvider.objects.filter(deleted_at__isnull=True).count(), 2)

    def test_preferred_ones_come_first_and_notes_stay_with_the_link(self):
        self.link(self.second, self.plumber, self.sparky)

        response = self.client.patch(
            self.url(self.second, str(self.sparky["id"])),
            {"is_recommended": True, "contract_notes": "Annual contract"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_recommended"])
        listed = self.client.get(self.url(self.second))
        self.assertEqual(self.names(listed), ["Zed Electrical", "Acme Plumbing"])
        self.assertEqual(listed.data[0]["contract_notes"], "Annual contract")

    def test_unlinking_keeps_the_contact_and_its_other_properties(self):
        self.link(self.first, self.plumber)
        self.link(self.second, self.plumber)

        response = self.client.delete(self.url(self.second, str(self.plumber["id"])))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.names(self.client.get(self.url(self.second))), [])
        self.assertEqual(self.names(self.client.get(self.url(self.first))), ["Acme Plumbing"])
        self.assertEqual(
            self.client.get(f"/api/landlord/providers/{self.plumber['id']}/").status_code, 200
        )

    def test_a_contact_can_be_linked_again_after_unlinking(self):
        self.link(self.first, self.plumber)
        self.client.delete(self.url(self.first, str(self.plumber["id"])))

        response = self.link(self.first, self.plumber)

        self.assertEqual(self.names(response), ["Acme Plumbing"])

    def test_another_landlords_property_or_contact_is_refused(self):
        amy_place = self.new_property(self.amy, address_line_1="9 Other Rd")
        amy_plumber = self.new_provider(self.amy, business_name="Amy's Pipes")

        self.as_user(self.lou)
        on_theirs = self.post(self.url(amy_place), {"provider_ids": [self.plumber["id"]]})
        theirs = self.post(self.url(self.first), {"provider_ids": [amy_plumber["id"]]})

        self.assertEqual(on_theirs.status_code, 404)
        self.assertEqual(theirs.status_code, 400)
        self.assertEqual(self.client.get(self.url(amy_place)).status_code, 404)

    def test_unlinking_something_never_linked_is_not_found(self):
        response = self.client.delete(self.url(self.first, str(self.plumber["id"])))

        self.assertEqual(response.status_code, 404)

    def test_tenants_are_refused(self):
        tina = self.make_user("tina@example.com", "TENANT", "Tina", "Ray")
        self.as_user(tina)

        self.assertEqual(self.client.get(self.url(self.first)).status_code, 403)
