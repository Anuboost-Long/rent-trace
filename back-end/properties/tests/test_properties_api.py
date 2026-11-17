from datetime import date

from accounts.models import User
from properties.models import Property, PropertyOwner, PropertyUnit
from tenancies.models import Tenancy
from users.tests.base import UsersApiTestCase

URL = "/api/properties/"


class PropertiesApiTestCase(UsersApiTestCase):
    def payload(self, owner, **extra):
        return {
            "address_line_1": "12 Smith St",
            "suburb": "Fitzroy",
            "state": "VIC",
            "postcode": "3065",
            "property_type": "HOUSE",
            "owner_id": owner.pk,
            **extra,
        }

    def make_property(self, owner, **extra):
        response = self.post(URL, self.payload(owner, **extra))
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def make_tenancy(self, unit):
        return Tenancy.objects.create(
            property_unit=unit,
            reference_no="T-1",
            tenancy_type="WHOLE_UNIT",
            start_date=date(2026, 1, 1),
        )


class CreatePropertyTests(PropertiesApiTestCase):
    def test_admin_creates_a_property_with_the_landlord_as_primary_owner(self):
        admin = self.sign_in_as_admin()
        landlord = self.make_user("lou@example.com", "LANDLORD", "Lou", "Reed")

        response = self.post(URL, self.payload(landlord, property_name="Smith House"))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["property_name"], "Smith House")
        self.assertEqual(response.data["owner"]["id"], landlord.pk)
        self.assertEqual(response.data["country"], "Australia")
        created = Property.objects.get()
        self.assertEqual(created.created_by, admin)
        ownership = PropertyOwner.objects.get()
        self.assertEqual((ownership.owner, ownership.is_primary_owner), (landlord, True))
        self.assertEqual(str(ownership.ownership_percentage), "100.00")

    def test_blank_optional_text_is_stored_as_null(self):
        self.sign_in_as_admin()
        landlord = self.make_user("lou@example.com", "LANDLORD")

        self.post(URL, self.payload(landlord, property_name="  ", address_line_2=""))

        created = Property.objects.get()
        self.assertIsNone(created.address_line_2)

    def test_the_owner_must_be_an_active_landlord(self):
        self.sign_in_as_admin()
        tenant = self.make_user("tina@example.com", "TENANT")

        response = self.post(URL, self.payload(tenant))

        self.assertEqual(response.status_code, 400)
        self.assertIn("owner_id", response.data)
        self.assertFalse(Property.objects.exists())

    def test_a_suspended_landlord_cannot_be_the_owner(self):
        self.sign_in_as_admin()
        landlord = self.make_user("lou@example.com", "LANDLORD")
        User.objects.filter(pk=landlord.pk).update(account_status="SUSPENDED")

        self.assertEqual(self.post(URL, self.payload(landlord)).status_code, 400)

    def test_the_state_must_be_a_known_australian_state(self):
        self.sign_in_as_admin()
        landlord = self.make_user("lou@example.com", "LANDLORD")

        response = self.post(URL, self.payload(landlord, state="Narnia"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("state", response.data)

    def test_an_unknown_property_type_is_rejected(self):
        self.sign_in_as_admin()
        landlord = self.make_user("lou@example.com", "LANDLORD")

        response = self.post(URL, self.payload(landlord, property_type="CASTLE"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("property_type", response.data)

    def test_view_only_admins_cannot_create(self):
        self.make_role("VIEWER", ["properties.admin_view"])
        self.sign_in_as_admin(roles=("VIEWER",))
        landlord = self.make_user("lou@example.com", "LANDLORD")

        self.assertEqual(self.post(URL, self.payload(landlord)).status_code, 403)

    def test_a_landlord_cannot_reach_the_admin_api(self):
        landlord = self.make_user("lou@example.com", "LANDLORD")
        self.sign_in_user(landlord)

        self.assertEqual(self.client.get(URL).status_code, 403)


class ListPropertiesTests(PropertiesApiTestCase):
    def test_lists_newest_first_with_owner_and_unit_count(self):
        self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD", "Lou", "Reed")
        first = self.make_property(lou, property_name="First")
        self.make_property(lou, property_name="Second")
        self.post(f"{URL}{first['id']}/units/", {"name": "Flat 1", "unit_type": "APARTMENT"})

        response = self.client.get(URL)

        names = [row["property_name"] for row in response.data["results"]]
        self.assertEqual(names, ["Second", "First"])
        counts = {row["property_name"]: row["unit_count"] for row in response.data["results"]}
        self.assertEqual(counts, {"First": 1, "Second": 0})
        self.assertEqual(response.data["results"][0]["owner"]["email"], "lou@example.com")

    def test_search_finds_by_suburb_and_by_owner_name(self):
        self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD", "Lou", "Reed")
        amy = self.make_user("amy@example.com", "LANDLORD", "Amy", "Wong")
        self.make_property(lou, suburb="Carlton")
        self.make_property(amy, suburb="Brunswick")

        by_suburb = self.client.get(URL, {"q": "carlton"})
        by_owner = self.client.get(URL, {"q": "wong"})

        self.assertEqual([r["suburb"] for r in by_suburb.data["results"]], ["Carlton"])
        self.assertEqual([r["suburb"] for r in by_owner.data["results"]], ["Brunswick"])

    def test_filters_by_status(self):
        self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD")
        made = self.make_property(lou)
        self.make_property(lou, suburb="Other")
        self.client.patch(f"{URL}{made['id']}/", {"property_status": "ARCHIVED"}, format="json")

        response = self.client.get(URL, {"status": "ARCHIVED"})

        self.assertEqual([r["id"] for r in response.data["results"]], [made["id"]])


class OwnerOptionsTests(PropertiesApiTestCase):
    def test_lists_only_active_landlords(self):
        self.sign_in_as_admin()
        self.make_user("lou@example.com", "LANDLORD", "Lou", "Reed")
        self.make_user("tina@example.com", "TENANT")
        gone = self.make_user("gone@example.com", "LANDLORD")
        User.objects.filter(pk=gone.pk).update(account_status="SUSPENDED")

        response = self.client.get(f"{URL}owner-options/")

        self.assertEqual([row["email"] for row in response.data], ["lou@example.com"])

    def test_filters_by_text(self):
        self.sign_in_as_admin()
        self.make_user("lou@example.com", "LANDLORD", "Lou", "Reed")
        self.make_user("amy@example.com", "LANDLORD", "Amy", "Wong")

        response = self.client.get(f"{URL}owner-options/", {"q": "amy"})

        self.assertEqual([row["email"] for row in response.data], ["amy@example.com"])


class PropertyDetailTests(PropertiesApiTestCase):
    def test_detail_shows_owners_and_units(self):
        self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD")
        made = self.make_property(lou, private_notes="Key under the mat")
        self.post(f"{URL}{made['id']}/units/", {"name": "Flat 1", "unit_type": "APARTMENT"})

        response = self.client.get(f"{URL}{made['id']}/")

        self.assertEqual(response.data["private_notes"], "Key under the mat")
        self.assertEqual([o["owner"]["id"] for o in response.data["owners"]], [lou.pk])
        self.assertEqual([u["name"] for u in response.data["units"]], ["Flat 1"])

    def test_unknown_property_is_404(self):
        self.sign_in_as_admin()

        self.assertEqual(self.client.get(f"{URL}999/").status_code, 404)

    def test_update_changes_only_the_fields_sent(self):
        admin = self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD")
        made = self.make_property(lou)

        response = self.client.patch(f"{URL}{made['id']}/", {"suburb": "Carlton"}, format="json")

        self.assertEqual(response.status_code, 200)
        saved = Property.objects.get()
        self.assertEqual((saved.suburb, saved.address_line_1), ("Carlton", "12 Smith St"))
        self.assertEqual((saved.updated_by, saved.row_version), (admin, 2))

    def test_view_only_admins_cannot_update_or_delete(self):
        self.sign_in_as_admin(super_admin=True)
        lou = self.make_user("lou@example.com", "LANDLORD")
        made = self.make_property(lou)
        self.make_role("VIEWER", ["properties.admin_view"])
        self.sign_in_as_admin(roles=("VIEWER",), email="viewer@example.com")

        patch = self.client.patch(f"{URL}{made['id']}/", {"suburb": "X"}, format="json")
        remove = self.client.delete(f"{URL}{made['id']}/")

        self.assertEqual((patch.status_code, remove.status_code), (403, 403))
        self.assertEqual(self.client.get(f"{URL}{made['id']}/").status_code, 200)


class DeletePropertyTests(PropertiesApiTestCase):
    def test_delete_hides_the_property_and_its_units(self):
        admin = self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD")
        made = self.make_property(lou)
        self.post(f"{URL}{made['id']}/units/", {"name": "Flat 1", "unit_type": "APARTMENT"})

        response = self.client.delete(f"{URL}{made['id']}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"{URL}{made['id']}/").status_code, 404)
        self.assertEqual(self.client.get(URL).data["count"], 0)
        removed = Property.objects.get()
        self.assertEqual(removed.deleted_by, admin)
        self.assertIsNotNone(PropertyUnit.objects.get().deleted_at)

    def test_a_property_with_tenancies_cannot_be_deleted(self):
        self.sign_in_as_admin()
        lou = self.make_user("lou@example.com", "LANDLORD")
        made = self.make_property(lou)
        unit = self.post(
            f"{URL}{made['id']}/units/", {"name": "Flat 1", "unit_type": "APARTMENT"}
        ).data
        self.make_tenancy(PropertyUnit.objects.get(pk=unit["id"]))

        response = self.client.delete(f"{URL}{made['id']}/")

        self.assertEqual(response.status_code, 409)
        self.assertIsNone(Property.objects.get().deleted_at)


class UnitTests(PropertiesApiTestCase):
    def setUp(self):
        super().setUp()
        self.admin = self.sign_in_as_admin()
        self.landlord = self.make_user("lou@example.com", "LANDLORD")
        self.made = self.make_property(self.landlord)
        self.units_url = f"{URL}{self.made['id']}/units/"

    def make_unit(self, **extra):
        return self.post(self.units_url, {"name": "Flat 1", "unit_type": "APARTMENT", **extra}).data

    def test_creates_a_unit_that_is_vacant_and_private_by_default(self):
        response = self.post(self.units_url, {"name": "Flat 1", "unit_type": "APARTMENT"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["occupancy_status"], "VACANT")
        self.assertFalse(response.data["is_public"])
        self.assertEqual(PropertyUnit.objects.get().created_by, self.admin)

    def test_unit_needs_a_name_and_a_known_type(self):
        response = self.post(self.units_url, {"unit_type": "TENT"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data), {"name", "unit_type"})

    def test_cannot_add_a_unit_to_a_missing_property(self):
        response = self.post(f"{URL}999/units/", {"name": "Flat 1", "unit_type": "APARTMENT"})

        self.assertEqual(response.status_code, 404)

    def test_updates_a_unit(self):
        unit = self.make_unit()

        response = self.client.patch(
            f"{self.units_url}{unit['id']}/", {"name": "Flat 2", "is_public": True}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        saved = PropertyUnit.objects.get()
        self.assertEqual((saved.name, saved.is_public, saved.row_version), ("Flat 2", True, 2))

    def test_a_unit_cannot_be_reached_through_another_property(self):
        unit = self.make_unit()
        other = self.make_property(self.landlord, suburb="Other")

        response = self.client.patch(
            f"{URL}{other['id']}/units/{unit['id']}/", {"name": "X"}, format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_deletes_a_unit(self):
        unit = self.make_unit()

        response = self.client.delete(f"{self.units_url}{unit['id']}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"{URL}{self.made['id']}/").data["units"], [])

    def test_a_unit_with_tenancies_cannot_be_deleted(self):
        unit = self.make_unit()
        self.make_tenancy(PropertyUnit.objects.get(pk=unit["id"]))

        response = self.client.delete(f"{self.units_url}{unit['id']}/")

        self.assertEqual(response.status_code, 409)
