from datetime import timedelta

from django.utils import timezone

from properties.models import Property, PropertyOwner, PropertyUnit
from properties.tests.test_properties_api import PropertiesApiTestCase

URL = "/api/landlord/properties/"
UNIT = {"name": "Flat 1", "unit_type": "APARTMENT"}


class LandlordApiTestCase(PropertiesApiTestCase):
    def setUp(self):
        super().setUp()
        self.lou = self.make_user("lou@example.com", "LANDLORD", "Lou", "Reed")
        self.amy = self.make_user("amy@example.com", "LANDLORD", "Amy", "Wong")

    def as_user(self, user):
        self.sign_in_user(user)

    def new_property(self, landlord, **extra):
        self.as_user(landlord)
        response = self.post(URL, self.fields(**extra))
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def fields(self, **extra):
        return {
            "address_line_1": "12 Smith St",
            "suburb": "Fitzroy",
            "state": "VIC",
            "postcode": "3065",
            "property_type": "HOUSE",
            **extra,
        }


class CreatePropertyTests(LandlordApiTestCase):
    def test_a_landlord_sets_up_a_property_and_becomes_its_primary_owner(self):
        self.as_user(self.lou)

        response = self.post(URL, self.fields(property_name="Smith House"))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["owner"]["id"], self.lou.pk)
        created = Property.objects.get()
        self.assertEqual(created.created_by, self.lou)
        ownership = PropertyOwner.objects.get()
        self.assertEqual((ownership.owner, ownership.is_primary_owner), (self.lou, True))

    def test_the_owner_cannot_be_chosen(self):
        self.as_user(self.lou)

        self.post(URL, self.fields(owner_id=self.amy.pk))

        self.assertEqual(PropertyOwner.objects.get().owner, self.lou)

    def test_bad_input_is_rejected_per_field(self):
        self.as_user(self.lou)

        response = self.post(URL, {"property_type": "CASTLE"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            set(response.data), {"address_line_1", "suburb", "state", "postcode", "property_type"}
        )

    def test_tenants_and_admins_cannot_use_the_landlord_api(self):
        tenant = self.make_user("tina@example.com", "TENANT")
        self.as_user(tenant)
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.assertEqual(self.post(URL, self.fields()).status_code, 403)

        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.assertEqual(self.post(URL, self.fields()).status_code, 403)
        self.assertFalse(Property.objects.exists())

    def test_signing_in_is_required(self):
        self.assertEqual(self.client.get(URL).status_code, 401)


class ListAndReadTests(LandlordApiTestCase):
    def test_a_landlord_only_sees_their_own_properties(self):
        mine = self.new_property(self.lou, suburb="Carlton")
        self.new_property(self.amy, suburb="Brunswick")
        self.as_user(self.lou)

        response = self.client.get(URL)

        self.assertEqual([row["id"] for row in response.data["results"]], [mine["id"]])
        self.assertEqual(response.data["count"], 1)

    def test_search_and_status_filter_stay_inside_their_own_properties(self):
        self.new_property(self.lou, suburb="Carlton")
        archived = self.new_property(self.lou, suburb="Fitzroy")
        self.new_property(self.amy, suburb="Carlton")
        self.as_user(self.lou)
        self.client.patch(f"{URL}{archived['id']}/", {"property_status": "ARCHIVED"}, format="json")

        by_text = self.client.get(URL, {"q": "carlton"})
        by_status = self.client.get(URL, {"status": "ARCHIVED"})

        self.assertEqual([r["suburb"] for r in by_text.data["results"]], ["Carlton"])
        self.assertEqual([r["id"] for r in by_status.data["results"]], [archived["id"]])

    def test_detail_shows_owners_units_and_private_notes(self):
        made = self.new_property(self.lou, private_notes="Key under the mat")
        self.post(f"{URL}{made['id']}/units/", UNIT)

        response = self.client.get(f"{URL}{made['id']}/")

        self.assertEqual(response.data["private_notes"], "Key under the mat")
        self.assertEqual([o["owner"]["id"] for o in response.data["owners"]], [self.lou.pk])
        self.assertEqual([u["name"] for u in response.data["units"]], ["Flat 1"])

    def test_someone_elses_property_is_not_found(self):
        theirs = self.new_property(self.amy)
        self.as_user(self.lou)

        self.assertEqual(self.client.get(f"{URL}{theirs['id']}/").status_code, 404)

    def test_a_co_owner_can_see_the_property(self):
        shared = self.new_property(self.amy)
        PropertyOwner.objects.create(
            property_id=shared["id"],
            owner=self.lou,
            ownership_percentage=50,
            valid_from=timezone.now(),
        )
        self.as_user(self.lou)

        self.assertEqual(self.client.get(f"{URL}{shared['id']}/").status_code, 200)

    def test_a_former_owner_loses_access(self):
        made = self.new_property(self.lou)
        now = timezone.now()
        PropertyOwner.objects.update(valid_from=now - timedelta(days=1), valid_to=now)

        self.assertEqual(self.client.get(f"{URL}{made['id']}/").status_code, 404)


class UpdatePropertyTests(LandlordApiTestCase):
    def test_a_landlord_edits_their_property_and_can_archive_it(self):
        made = self.new_property(self.lou)

        response = self.client.patch(
            f"{URL}{made['id']}/",
            {"suburb": "Carlton", "property_status": "ARCHIVED"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        saved = Property.objects.get()
        self.assertEqual((saved.suburb, saved.property_status), ("Carlton", "ARCHIVED"))
        self.assertEqual((saved.updated_by, saved.row_version), (self.lou, 2))

    def test_someone_elses_property_cannot_be_edited(self):
        theirs = self.new_property(self.amy)
        self.as_user(self.lou)

        response = self.client.patch(f"{URL}{theirs['id']}/", {"suburb": "X"}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Property.objects.get().suburb, "Fitzroy")

    def test_a_landlord_cannot_delete_a_property(self):
        made = self.new_property(self.lou)

        self.assertEqual(self.client.delete(f"{URL}{made['id']}/").status_code, 403)
        self.assertIsNone(Property.objects.get().deleted_at)


class UnitTests(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        self.made = self.new_property(self.lou)
        self.units_url = f"{URL}{self.made['id']}/units/"

    def make_unit(self):
        return self.post(self.units_url, UNIT).data

    def test_a_landlord_adds_edits_and_removes_a_unit(self):
        unit = self.make_unit()
        self.assertEqual(PropertyUnit.objects.get().created_by, self.lou)

        edited = self.client.patch(
            f"{self.units_url}{unit['id']}/", {"name": "Flat 2"}, format="json"
        )
        removed = self.client.delete(f"{self.units_url}{unit['id']}/")

        self.assertEqual((edited.status_code, removed.status_code), (200, 204))
        self.assertEqual(self.client.get(f"{URL}{self.made['id']}/").data["units"], [])

    def test_units_on_someone_elses_property_are_not_found(self):
        theirs = self.new_property(self.amy)
        their_unit = self.post(f"{URL}{theirs['id']}/units/", UNIT).data
        self.as_user(self.lou)

        add = self.post(f"{URL}{theirs['id']}/units/", UNIT)
        edit = self.client.patch(
            f"{URL}{theirs['id']}/units/{their_unit['id']}/", {"name": "X"}, format="json"
        )
        remove = self.client.delete(f"{URL}{theirs['id']}/units/{their_unit['id']}/")

        self.assertEqual((add.status_code, edit.status_code, remove.status_code), (404, 404, 404))
        self.assertEqual(PropertyUnit.objects.get().name, "Flat 1")

    def test_a_unit_with_tenancies_cannot_be_removed(self):
        unit = self.make_unit()
        self.make_tenancy(PropertyUnit.objects.get(pk=unit["id"]))

        response = self.client.delete(f"{self.units_url}{unit['id']}/")

        self.assertEqual(response.status_code, 409)
