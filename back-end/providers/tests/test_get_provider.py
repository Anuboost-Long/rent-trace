from providers.tests.base import URL, ProvidersApiTestCase


class GetProviderTests(ProvidersApiTestCase):
    def test_landlord_reads_their_provider(self):
        made = self.new_provider(category_codes=["ELECTRICAL"])

        response = self.client.get(f"{URL}{made['id']}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["categories"][0]["code"], "ELECTRICAL")

    def test_another_landlords_provider_is_not_found(self):
        made = self.new_provider(self.lou)
        self.as_user(self.amy)

        response = self.client.get(f"{URL}{made['id']}/")

        self.assertEqual(response.status_code, 404)
