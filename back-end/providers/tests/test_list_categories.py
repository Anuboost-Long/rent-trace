from providers.tests.base import URL, ProvidersApiTestCase


class ListCategoriesTests(ProvidersApiTestCase):
    def test_landlord_sees_the_seeded_categories_by_name(self):
        self.as_user(self.lou)

        response = self.client.get(f"{URL}categories/")

        self.assertEqual(response.status_code, 200)
        names = [row["name"] for row in response.data]
        self.assertEqual(names, sorted(names))
        self.assertIn({"code": "PLUMBING", "name": "Plumbing"}, response.data)
        self.assertEqual(len(response.data), 7)
