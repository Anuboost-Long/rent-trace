from django.db import connection
from django.test.utils import CaptureQueriesContext

from providers.tests.base import URL, ProvidersApiTestCase


class ListProvidersTests(ProvidersApiTestCase):
    def test_lists_only_my_providers_by_name(self):
        self.new_provider(self.lou, business_name="Zed Electrical")
        self.new_provider(self.lou, business_name="Acme Plumbing")
        self.new_provider(self.amy, business_name="Amy's Locksmith")
        self.as_user(self.lou)

        response = self.client.get(URL)

        names = [row["business_name"] for row in response.data["results"]]
        self.assertEqual(names, ["Acme Plumbing", "Zed Electrical"])

    def test_filters_by_words_and_by_category(self):
        self.new_provider(business_name="Acme Plumbing", category_codes=["PLUMBING"])
        self.new_provider(
            business_name="Zed Electrical", contact_name="Pat", category_codes=["ELECTRICAL"]
        )
        self.as_user(self.lou)

        by_name = self.client.get(URL, {"q": "acme"}).data["results"]
        by_contact = self.client.get(URL, {"q": "pat"}).data["results"]
        by_category = self.client.get(URL, {"category": "ELECTRICAL"}).data["results"]

        self.assertEqual([r["business_name"] for r in by_name], ["Acme Plumbing"])
        self.assertEqual([r["business_name"] for r in by_contact], ["Zed Electrical"])
        self.assertEqual([r["business_name"] for r in by_category], ["Zed Electrical"])

    def test_the_number_of_queries_does_not_grow_with_the_list(self):
        homes = [self.new_property(self.lou) for _ in range(2)]
        links = [self.link(home["id"]) for home in homes]
        self.new_provider(category_codes=["PLUMBING", "PESTS"], properties=links)
        with CaptureQueriesContext(connection) as one:
            self.client.get(URL)
        for index in range(4):
            self.new_provider(
                business_name=f"Extra {index}",
                category_codes=["GENERAL", "PESTS"],
                properties=links,
            )

        with CaptureQueriesContext(connection) as five:
            response = self.client.get(URL)

        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(len(five), len(one))
