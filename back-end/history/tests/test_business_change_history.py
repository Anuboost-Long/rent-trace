from history.models import BusinessChangeHistory
from properties.models import Property, PropertyUnit
from tenancies.models import Tenancy, TenancyTermChange
from tenancies.tests.base import LANDLORD_URL, TenancyApiTestCase

PROPERTIES = "/api/landlord/properties/"
TENANT_TENANCIES = "/api/tenant/tenancies/"


class BusinessChangeHistoryTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.place = self.unit.property

    def rows(self, **filters):
        return BusinessChangeHistory.objects.filter(**filters).order_by("sequence_no")

    def patch(self, url, changes, user=None):
        self.as_user(user or self.lou)
        return self.client.patch(url, changes, format="json")

    def test_editing_a_property_records_only_what_changed(self):
        response = self.patch(
            f"{PROPERTIES}{self.place.pk}/",
            {"property_name": "Smith House", "suburb": self.place.suburb},
        )

        self.assertEqual(response.status_code, 200, response.data)
        row = self.rows(action="UPDATE_PROPERTY").get()
        self.assertEqual(row.after_values, {"property_name": "Smith House"})
        self.assertEqual(row.before_values, {"property_name": self.place.property_name})
        self.assertEqual((row.created_by, row.target.property), (self.lou, self.place))

    def test_a_save_that_changes_nothing_writes_nothing(self):
        self.patch(f"{PROPERTIES}{self.place.pk}/", {"suburb": self.place.suburb})

        self.assertFalse(BusinessChangeHistory.objects.exists())

    def test_rent_on_a_unit_is_recorded_as_plain_values(self):
        self.patch(
            f"{PROPERTIES}{self.place.pk}/units/{self.unit.pk}/",
            {"rent_amount": "450.00", "rent_frequency": "WEEKLY"},
        )

        row = self.rows(action="UPDATE_UNIT").get()
        self.assertEqual(row.after_values, {"rent_amount": "450.00", "rent_frequency": "WEEKLY"})
        self.assertEqual(row.target.property_unit, self.unit)

    def test_each_change_gets_the_next_sequence_number(self):
        self.patch(f"{PROPERTIES}{self.place.pk}/", {"property_name": "One"})
        self.patch(f"{PROPERTIES}{self.place.pk}/", {"property_name": "Two"})

        self.assertEqual(
            list(self.rows(target__property=self.place).values_list("sequence_no", "after_values")),
            [(1, {"property_name": "One"}), (2, {"property_name": "Two"})],
        )

    def test_listing_status_and_occupancy_are_recorded(self):
        self.as_user(self.lou)
        self.post(
            f"{PROPERTIES}{self.place.pk}/units/{self.unit.pk}/occupancy/",
            {"occupancy_status": "UNAVAILABLE"},
        )

        row = self.rows(action="CHANGE_OCCUPANCY").get()
        self.assertEqual(row.after_values, {"occupancy_status": "UNAVAILABLE"})

    def test_removing_a_unit_and_a_property_are_recorded(self):
        self.as_user(self.lou)
        self.assertEqual(
            self.client.delete(f"{PROPERTIES}{self.place.pk}/units/{self.unit.pk}/").status_code,
            204,
        )
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(self.client.delete(f"/api/properties/{self.place.pk}/").status_code, 204)

        self.assertEqual(self.rows(action="DELETE_UNIT").get().after_values, {"deleted": True})
        self.assertEqual(self.rows(action="DELETE_PROPERTY").get().after_values, {"deleted": True})
        self.assertTrue(PropertyUnit.objects.get(pk=self.unit.pk).deleted_at)
        self.assertTrue(Property.objects.get(pk=self.place.pk).deleted_at)

    def test_tenancy_edits_record_dates_notes_and_rent_that_applied(self):
        tenancy = self.new_tenancy()
        self.patch(
            f"{LANDLORD_URL}{tenancy['id']}/",
            {"notes": "Key under the mat", "rent_amount": "450", "rent_frequency": "WEEKLY"},
        )

        row = self.rows(action="UPDATE_TENANCY").get()
        self.assertEqual(row.after_values["notes"], "Key under the mat")
        self.assertEqual(row.after_values["rent_amount"], "450.00")
        self.assertEqual(row.target.tenancy_id, tenancy["id"])

    def test_a_rent_rise_is_recorded_only_when_every_tenant_approves_it(self):
        tenancy = self.new_tenancy()
        self.patch(
            f"{LANDLORD_URL}{tenancy['id']}/", {"rent_amount": "450", "rent_frequency": "WEEKLY"}
        )
        Tenancy.objects.filter(pk=tenancy["id"]).update(status="ACTIVE")
        self.add_tenant(tenancy["id"], self.tina)
        self.patch(f"{LANDLORD_URL}{tenancy['id']}/", {"rent_amount": "500"})
        self.assertFalse(self.rows(action="APPLY_TERM_CHANGE").exists())
        proposal = TenancyTermChange.objects.get(tenancy_id=tenancy["id"], status="PENDING")

        self.as_user(self.tina)
        self.post(f"{TENANT_TENANCIES}{tenancy['id']}/changes/{proposal.pk}/approve/")

        row = self.rows(action="APPLY_TERM_CHANGE").get()
        self.assertEqual(
            (row.before_values, row.after_values),
            ({"rent_amount": "450.00"}, {"rent_amount": "500.00"}),
        )
        self.assertEqual(row.created_by, self.tina)
