from properties.tests.test_landlord_properties_api import URL as LANDLORD_URL
from properties.tests.test_landlord_properties_api import LandlordApiTestCase


class UnitMaxOccupantsTests(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        self.made = self.new_property(self.lou)
        self.units_url = f"{LANDLORD_URL}{self.made['id']}/units/"

    def unit(self, **extra):
        return {"name": "Flat 1", "unit_type": "APARTMENT", **extra}

    def test_a_unit_can_have_a_maximum_number_of_people(self):
        response = self.post(self.units_url, self.unit(max_occupants=4))

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["max_occupants"], 4)

    def test_no_limit_is_the_default(self):
        self.assertIsNone(self.post(self.units_url, self.unit()).data["max_occupants"])

    def test_the_limit_must_be_a_whole_number_of_at_least_one(self):
        for bad in (0, -2, 101, "many"):
            with self.subTest(value=bad):
                response = self.post(self.units_url, self.unit(max_occupants=bad))
                self.assertEqual(response.status_code, 400)
                self.assertIn("max_occupants", response.data)

    def test_the_limit_can_be_changed_and_cleared(self):
        unit = self.post(self.units_url, self.unit(max_occupants=2)).data
        url = f"{self.units_url}{unit['id']}/"

        raised = self.client.patch(url, {"max_occupants": 5}, format="json")
        cleared = self.client.patch(url, {"max_occupants": None}, format="json")

        self.assertEqual(raised.data["max_occupants"], 5)
        self.assertIsNone(cleared.data["max_occupants"])

    def test_the_detail_carries_the_limit(self):
        self.post(self.units_url, self.unit(max_occupants=3))

        detail = self.client.get(f"{LANDLORD_URL}{self.made['id']}/")

        self.assertEqual(detail.data["units"][0]["max_occupants"], 3)
