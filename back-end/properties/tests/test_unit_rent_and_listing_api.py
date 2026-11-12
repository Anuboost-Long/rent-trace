from properties.models import Property, PropertyUnit
from properties.tests.test_landlord_properties_api import URL as LANDLORD_URL
from properties.tests.test_landlord_properties_api import LandlordApiTestCase
from properties.tests.test_properties_api import URL as ADMIN_URL


class RentTests(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        self.made = self.new_property(self.lou)
        self.units_url = f"{LANDLORD_URL}{self.made['id']}/units/"

    def unit(self, **extra):
        return {"name": "Room 1", "unit_type": "ROOM", **extra}

    def test_a_unit_can_have_a_rent(self):
        response = self.post(
            self.units_url, self.unit(rent_amount="650.00", rent_frequency="WEEKLY")
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(
            (response.data["rent_amount"], response.data["rent_frequency"]), ("650.00", "WEEKLY")
        )

    def test_a_unit_without_rent_is_fine(self):
        response = self.post(self.units_url, self.unit())

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data["rent_amount"])

    def test_rent_needs_both_an_amount_and_a_frequency(self):
        no_frequency = self.post(self.units_url, self.unit(rent_amount="500"))
        no_amount = self.post(self.units_url, self.unit(rent_frequency="MONTHLY"))

        self.assertIn("rent_frequency", no_frequency.data)
        self.assertIn("rent_amount", no_amount.data)
        self.assertFalse(PropertyUnit.objects.exists())

    def test_rent_must_be_positive_and_a_known_frequency(self):
        zero = self.post(self.units_url, self.unit(rent_amount="0", rent_frequency="WEEKLY"))
        odd = self.post(self.units_url, self.unit(rent_amount="10", rent_frequency="DAILY"))

        self.assertIn("rent_amount", zero.data)
        self.assertIn("rent_frequency", odd.data)

    def test_rent_can_be_changed_and_cleared(self):
        unit = self.post(self.units_url, self.unit(rent_amount="650", rent_frequency="WEEKLY")).data

        changed = self.client.patch(
            f"{self.units_url}{unit['id']}/", {"rent_amount": "700"}, format="json"
        )
        cleared = self.client.patch(
            f"{self.units_url}{unit['id']}/",
            {"rent_amount": None, "rent_frequency": None},
            format="json",
        )

        self.assertEqual(
            (changed.data["rent_amount"], changed.data["rent_frequency"]), ("700.00", "WEEKLY")
        )
        self.assertEqual(
            (cleared.data["rent_amount"], cleared.data["rent_frequency"]), (None, None)
        )

    def test_clearing_only_the_amount_is_rejected(self):
        unit = self.post(self.units_url, self.unit(rent_amount="650", rent_frequency="WEEKLY")).data

        response = self.client.patch(
            f"{self.units_url}{unit['id']}/", {"rent_amount": None}, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PropertyUnit.objects.get().rent_amount, 650)


class ListingStatusTests(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        self.made = self.new_property(self.lou)
        self.url = f"{LANDLORD_URL}{self.made['id']}/listing/"

    def add_unit(self, **extra):
        return self.post(
            f"{LANDLORD_URL}{self.made['id']}/units/",
            {"name": "Room 1", "unit_type": "ROOM", **extra},
        ).data

    def set_status(self, value, url=None):
        return self.client.post(url or self.url, {"listing_status": value}, format="json")

    def test_a_landlord_can_list_a_property_that_has_a_public_unit(self):
        self.add_unit(is_public=True)

        response = self.set_status("AVAILABLE")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["listing_status"], "AVAILABLE")
        self.assertEqual(Property.objects.get().listing_status, "AVAILABLE")

    def test_listing_needs_at_least_one_public_unit(self):
        self.add_unit(is_public=False)

        response = self.set_status("AVAILABLE")

        self.assertEqual(response.status_code, 400)
        self.assertIn("listing_status", response.data)
        self.assertEqual(Property.objects.get().listing_status, "DRAFT")

    def test_an_inactive_property_cannot_be_listed(self):
        self.add_unit(is_public=True)
        self.client.patch(
            f"{LANDLORD_URL}{self.made['id']}/", {"property_status": "ARCHIVED"}, format="json"
        )

        self.assertEqual(self.set_status("AVAILABLE").status_code, 400)

    def test_a_landlord_can_unlist_without_the_listing_conditions(self):
        self.add_unit(is_public=True)
        self.set_status("AVAILABLE")

        self.assertEqual(self.set_status("UNLISTED").status_code, 200)
        self.assertEqual(self.set_status("DRAFT").status_code, 200)

    def test_a_landlord_cannot_suspend_or_archive_a_listing(self):
        self.assertEqual(self.set_status("SUSPENDED").status_code, 400)
        self.assertEqual(self.set_status("ARCHIVED").status_code, 400)

    def test_someone_elses_property_is_not_found(self):
        self.as_user(self.amy)

        self.assertEqual(self.set_status("UNLISTED").status_code, 404)

    def test_tenants_cannot_change_a_listing(self):
        self.as_user(self.make_user("tina@example.com", "TENANT"))

        self.assertEqual(self.set_status("UNLISTED").status_code, 403)

    def test_an_admin_can_suspend_and_a_landlord_cannot_undo_it(self):
        self.add_unit(is_public=True)
        admin_url = f"{ADMIN_URL}{self.made['id']}/listing/"
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        suspended = self.set_status("SUSPENDED", admin_url)
        self.as_user(self.lou)
        undone = self.set_status("AVAILABLE")

        self.assertEqual((suspended.status_code, undone.status_code), (200, 403))
        self.assertEqual(Property.objects.get().listing_status, "SUSPENDED")

    def test_an_admin_can_restore_a_suspended_listing(self):
        self.add_unit(is_public=True)
        admin_url = f"{ADMIN_URL}{self.made['id']}/listing/"
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.set_status("SUSPENDED", admin_url)

        restored = self.set_status("AVAILABLE", admin_url)

        self.assertEqual(restored.status_code, 200)
