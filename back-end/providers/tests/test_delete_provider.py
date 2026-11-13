from providers.models import PropertyServiceProvider, ServiceProvider
from providers.tests.base import URL, ProvidersApiTestCase


class DeleteProviderTests(ProvidersApiTestCase):
    def test_removes_the_provider_and_its_links(self):
        home = self.new_property(self.lou)
        made = self.new_provider(category_codes=["PESTS"], properties=[self.link(home["id"])])

        response = self.client.delete(f"{URL}{made['id']}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"{URL}{made['id']}/").status_code, 404)
        self.assertIsNotNone(ServiceProvider.objects.get().deleted_at)
        self.assertFalse(PropertyServiceProvider.objects.filter(deleted_at__isnull=True).exists())

    def test_another_landlords_provider_is_not_found(self):
        made = self.new_provider(self.lou)
        self.as_user(self.amy)

        response = self.client.delete(f"{URL}{made['id']}/")

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(ServiceProvider.objects.get().deleted_at)
