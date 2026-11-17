from users.tests.base import UsersApiTestCase

STATES_URL = "/api/locations/states/"
SUBURBS_URL = "/api/locations/suburbs/"


class LocationsApiTests(UsersApiTestCase):
    def test_lists_the_eight_states_and_territories(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        response = self.client.get(STATES_URL)

        self.assertEqual(
            [row["code"] for row in response.data],
            ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"],
        )
        self.assertEqual(response.data[6], {"code": "VIC", "name": "Victoria"})

    def test_suburbs_come_only_from_the_chosen_state(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        victoria = self.client.get(SUBURBS_URL, {"state": "VIC", "q": "carlton"})
        new_south_wales = self.client.get(SUBURBS_URL, {"state": "NSW", "q": "carlton"})

        self.assertIn({"suburb": "Carlton", "postcode": "3053"}, victoria.data)
        self.assertNotIn("3053", [row["postcode"] for row in new_south_wales.data])
        self.assertTrue(all(row["postcode"][0] == "3" for row in victoria.data))

    def test_search_matches_any_part_of_the_name_and_ranks_prefixes_first(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        response = self.client.get(SUBURBS_URL, {"state": "VIC", "q": "kilda"})
        names = [row["suburb"] for row in response.data]
        prefix = self.client.get(SUBURBS_URL, {"state": "VIC", "q": "st k"})

        self.assertIn("St Kilda", names)
        self.assertEqual(prefix.data[0]["suburb"].lower()[:4], "st k")

    def test_search_is_case_insensitive_and_titles_names_properly(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        response = self.client.get(SUBURBS_URL, {"state": "ACT", "q": "O'CONNOR"})

        self.assertEqual(response.data[0]["suburb"], "O'Connor")

    def test_limit_caps_the_results(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        response = self.client.get(SUBURBS_URL, {"state": "NSW", "limit": 5})

        self.assertEqual(len(response.data), 5)

    def test_without_a_search_it_lists_the_first_suburbs_of_the_state(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        response = self.client.get(SUBURBS_URL, {"state": "TAS"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 50)

    def test_an_unknown_state_is_rejected(self):
        self.sign_in_user(self.make_user("lou@example.com", "LANDLORD"))

        self.assertEqual(self.client.get(SUBURBS_URL, {"state": "XX"}).status_code, 400)
        self.assertEqual(self.client.get(SUBURBS_URL).status_code, 400)

    def test_signing_in_is_required(self):
        self.assertEqual(self.client.get(STATES_URL).status_code, 401)
        self.assertEqual(self.client.get(SUBURBS_URL, {"state": "VIC"}).status_code, 401)
