from datetime import date

from properties.models import PropertyUnit
from properties.tests.test_landlord_properties_api import URL as LANDLORD_URL
from properties.tests.test_landlord_properties_api import LandlordApiTestCase
from properties.tests.test_properties_api import URL as ADMIN_URL
from properties.tests.test_properties_api import PropertiesApiTestCase
from tenancies.models import Tenancy


class AdminUnitOccupancyTests(PropertiesApiTestCase):
    def setUp(self):
        super().setUp()
        self.sign_in_as_admin()
        self.landlord = self.make_user("lou@example.com", "LANDLORD")
        self.made = self.make_property(self.landlord)
        self.unit = PropertyUnit.objects.create(
            property_id=self.made["id"], name="Flat 1", unit_type="APARTMENT"
        )
        self.url = f"{ADMIN_URL}{self.made['id']}/units/{self.unit.pk}/occupancy/"

    def test_marks_a_vacant_unit_unavailable(self):
        response = self.post(self.url, {"occupancy_status": "UNAVAILABLE"})

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["occupancy_status"], "UNAVAILABLE")

    def test_marks_a_vacant_unit_partially_occupied(self):
        response = self.post(self.url, {"occupancy_status": "PARTIALLY_OCCUPIED"})

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["occupancy_status"], "PARTIALLY_OCCUPIED")

    def test_occupied_cannot_be_set_by_hand(self):
        response = self.post(self.url, {"occupancy_status": "OCCUPIED"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("occupancy_status", response.data)

    def test_refused_while_the_unit_has_a_current_tenant(self):
        Tenancy.objects.create(
            property_unit=self.unit,
            reference_no="T-1",
            tenancy_type="WHOLE_UNIT",
            status="ACTIVE",
            start_date=date(2026, 1, 1),
        )

        response = self.post(self.url, {"occupancy_status": "UNAVAILABLE"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("occupancy_status", response.data)
        self.assertEqual(PropertyUnit.objects.get(pk=self.unit.pk).occupancy_status, "VACANT")

    def test_a_draft_tenancy_does_not_block_the_change(self):
        self.make_tenancy(self.unit)

        response = self.post(self.url, {"occupancy_status": "UNAVAILABLE"})

        self.assertEqual(response.status_code, 200, response.data)


class LandlordUnitOccupancyTests(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        self.made = self.new_property(self.lou)
        self.unit = PropertyUnit.objects.create(
            property_id=self.made["id"], name="Flat 1", unit_type="APARTMENT"
        )
        self.url = f"{LANDLORD_URL}{self.made['id']}/units/{self.unit.pk}/occupancy/"

    def test_a_landlord_can_mark_their_own_unit_unavailable(self):
        response = self.post(self.url, {"occupancy_status": "UNAVAILABLE"})

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["occupancy_status"], "UNAVAILABLE")

    def test_a_landlord_cannot_reach_another_landlords_unit(self):
        other = self.new_property(self.amy)
        unit = PropertyUnit.objects.create(
            property_id=other["id"], name="Flat 2", unit_type="APARTMENT"
        )

        self.as_user(self.lou)
        response = self.post(
            f"{LANDLORD_URL}{other['id']}/units/{unit.pk}/occupancy/",
            {"occupancy_status": "UNAVAILABLE"},
        )

        self.assertEqual(response.status_code, 404)
