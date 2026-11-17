from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from notifications.models import Notification
from tenancies.models import Tenancy
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TenancyApiTestCase


class UpdateTenancyTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.today = timezone.now().date()
        self.tenancy = self.new_tenancy()

    def edit(self, changes, tenancy=None, url=LANDLORD_URL, user=None):
        self.as_user(user or self.lou)
        return self.client.patch(f"{url}{(tenancy or self.tenancy)['id']}/", changes, format="json")

    def row(self, tenancy=None):
        return Tenancy.objects.get(pk=(tenancy or self.tenancy)["id"])

    def move_to_active(self, tenancy=None, days_ago=10, end_in=None):
        update = {"status": "ACTIVE", "start_date": self.today - timedelta(days=days_ago)}
        update["end_date"] = self.today + timedelta(days=end_in) if end_in else None
        Tenancy.objects.filter(pk=(tenancy or self.tenancy)["id"]).update(**update)

    def join(self, tenancy=None, user=None):
        return self.add_tenant((tenancy or self.tenancy)["id"], user or self.tina)

    def test_a_landlord_sets_rent_bond_dates_and_notes_on_a_draft(self):
        response = self.edit(
            {
                "rent_amount": "450.00",
                "rent_frequency": "WEEKLY",
                "bond_amount": "1800",
                "start_date": "2026-12-08",
                "end_date": "2027-06-08",
                "notes": "Key under the mat",
            }
        )

        self.assertEqual(response.status_code, 200, response.data)
        saved = self.row()
        self.assertEqual(
            (saved.rent_amount, saved.rent_frequency, saved.bond_amount),
            (Decimal("450.00"), "WEEKLY", Decimal("1800.00")),
        )
        self.assertEqual((str(saved.start_date), str(saved.end_date)), ("2026-12-08", "2027-06-08"))
        self.assertEqual((saved.notes, saved.updated_by), ("Key under the mat", self.lou))
        self.assertEqual(response.data["rent_amount"], "450.00")
        self.assertEqual(response.data["currency"], "AUD")

    def test_what_is_left_out_stays_as_it_was(self):
        self.edit({"rent_amount": "400", "rent_frequency": "FORTNIGHTLY", "notes": "A"})

        self.edit({"bond_amount": "1000"})

        saved = self.row()
        self.assertEqual(
            (saved.rent_amount, saved.rent_frequency, saved.notes),
            (Decimal("400.00"), "FORTNIGHTLY", "A"),
        )
        self.assertEqual(saved.bond_amount, Decimal("1000.00"))

    def test_rent_needs_both_an_amount_and_a_frequency(self):
        for body in ({"rent_amount": "400"}, {"rent_frequency": "WEEKLY"}):
            with self.subTest(body=body):
                self.assertEqual(self.edit(body).status_code, 400)
        self.assertIsNone(self.row().rent_amount)

    def test_clearing_rent_needs_both_cleared(self):
        self.edit({"rent_amount": "400", "rent_frequency": "WEEKLY"})

        half = self.edit({"rent_amount": None})
        both = self.edit({"rent_amount": None, "rent_frequency": None})

        self.assertEqual(half.status_code, 400)
        self.assertEqual(both.status_code, 200)
        self.assertIsNone(self.row().rent_amount)

    def test_amounts_must_be_positive_and_the_frequency_known(self):
        for body in (
            {"rent_amount": "0", "rent_frequency": "WEEKLY"},
            {"rent_amount": "-5", "rent_frequency": "WEEKLY"},
            {"bond_amount": "0"},
            {"rent_amount": "400", "rent_frequency": "DAILY"},
        ):
            with self.subTest(body=body):
                self.assertEqual(self.edit(body).status_code, 400)

    def test_the_end_date_must_be_after_the_start_date(self):
        self.assertEqual(self.edit({"end_date": "2026-12-01"}).status_code, 400)
        self.assertEqual(
            self.edit({"start_date": "2027-01-01", "end_date": "2026-12-20"}).status_code, 400
        )
        self.assertEqual(self.edit({"start_date": "2026-12-05"}).status_code, 200)

    def test_an_active_tenancy_keeps_its_start_date(self):
        self.move_to_active()

        response = self.edit({"start_date": str(self.today - timedelta(days=3))})

        self.assertEqual(response.status_code, 400)
        self.assertIn("start_date", response.data)

    def test_an_active_tenancy_can_change_rent_notes_and_a_future_end_date(self):
        self.move_to_active()
        later = self.today + timedelta(days=90)

        response = self.edit(
            {"rent_amount": "500", "rent_frequency": "WEEKLY", "end_date": str(later)}
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.row().end_date, later)

    def test_an_active_tenancy_cannot_get_an_end_date_in_the_past(self):
        self.move_to_active()

        response = self.edit({"end_date": str(self.today - timedelta(days=1))})

        self.assertEqual(response.status_code, 400)
        self.assertIn("End tenancy", str(response.data))

    def test_a_changed_period_cannot_overlap_another_active_tenancy_on_the_unit(self):
        self.move_to_active(days_ago=100, end_in=30)
        other = self.new_tenancy(start_date=str(self.today + timedelta(days=60)))
        Tenancy.objects.filter(pk=other["id"]).update(status="ACTIVE")

        blocked = self.edit({"end_date": str(self.today + timedelta(days=90))})

        self.assertEqual(blocked.status_code, 400)
        self.assertIn("active tenancy", str(blocked.data))
        self.assertEqual(self.row().end_date, self.today + timedelta(days=30))

    def test_ended_and_cancelled_tenancies_cannot_be_edited(self):
        for status in ("ENDED", "CANCELLED"):
            with self.subTest(status=status):
                Tenancy.objects.filter(pk=self.tenancy["id"]).update(status=status)
                response = self.edit({"notes": "x"})
                self.assertEqual(response.status_code, 400)
                self.assertIn(status.lower(), str(response.data))

    def test_tenants_are_told_when_the_dates_change_and_the_text_has_no_amounts(self):
        self.join()

        self.edit({"end_date": "2027-06-01"})

        (row,) = Notification.objects.filter(recipient=self.tina)
        self.assertEqual((row.kind, row.subject_id), ("TENANCY_TERMS_CHANGED", self.tenancy["id"]))
        self.assertNotIn("$", row.title + row.body)

    def test_tenants_are_told_when_the_rent_goes_down_and_it_applies_at_once(self):
        self.edit({"rent_amount": "450", "rent_frequency": "WEEKLY"})
        self.join()

        response = self.edit({"rent_amount": "400", "rent_frequency": "WEEKLY"})

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.row().rent_amount, Decimal("400.00"))
        (row,) = Notification.objects.filter(recipient=self.tina)
        self.assertEqual(row.kind, "TENANCY_TERMS_CHANGED")
        self.assertNotIn("400", row.title + row.body)

    def test_a_notes_only_change_and_an_unchanged_value_tell_nobody(self):
        self.edit({"rent_amount": "450", "rent_frequency": "WEEKLY"})
        self.join()
        before = Notification.objects.count()

        self.edit({"notes": "Private note"})
        self.edit({"rent_amount": "450", "rent_frequency": "WEEKLY"})

        self.assertEqual(Notification.objects.count(), before)

    def test_a_tenancy_with_no_tenants_makes_no_notification(self):
        self.edit({"rent_amount": "450", "rent_frequency": "WEEKLY"})

        self.assertFalse(Notification.objects.exists())

    def test_tenants_never_see_the_notes(self):
        self.join()
        self.edit({"notes": "Landlord only"})

        self.as_user(self.tina)
        mine = self.client.get(f"/api/tenant/tenancies/{self.tenancy['id']}/")

        self.assertNotIn("Landlord only", str(mine.data))
        self.assertNotIn("notes", mine.data)

    def test_another_landlords_tenancy_is_not_found_and_tenants_are_refused(self):
        self.assertEqual(self.edit({"notes": "x"}, user=self.amy).status_code, 404)
        self.assertEqual(self.edit({"notes": "x"}, user=self.tina).status_code, 403)
        self.assertIsNone(self.row().notes)

    def test_an_admin_can_edit_any_tenancy(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        response = self.client.patch(
            f"{ADMIN_URL}{self.tenancy['id']}/",
            {"rent_amount": "600", "rent_frequency": "MONTHLY"},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.row().rent_frequency, "MONTHLY")


class CreateTenancyTermsTests(TenancyApiTestCase):
    def create(self, **extra):
        self.as_user(self.lou)
        return self.post(
            LANDLORD_URL, {"property_unit_id": self.unit.pk, "start_date": "2026-12-01", **extra}
        )

    def test_a_tenancy_can_start_with_rent_and_bond(self):
        response = self.create(rent_amount="450", rent_frequency="WEEKLY", bond_amount="1800")

        self.assertEqual(response.status_code, 201, response.data)
        saved = Tenancy.objects.get()
        self.assertEqual(
            (saved.rent_amount, saved.rent_frequency, saved.bond_amount),
            (Decimal("450.00"), "WEEKLY", Decimal("1800.00")),
        )

    def test_terms_are_optional_and_validated_the_same_way(self):
        self.assertEqual(self.create().status_code, 201)
        self.assertEqual(self.create(rent_amount="450").status_code, 400)
        self.assertEqual(self.create(rent_amount="0", rent_frequency="WEEKLY").status_code, 400)

    def test_the_tenancy_keeps_its_own_rent_when_the_unit_rent_changes(self):
        made = self.create(rent_amount="450", rent_frequency="WEEKLY").data
        self.unit.rent_amount, self.unit.rent_frequency = Decimal("999"), "WEEKLY"
        self.unit.save()

        self.assertEqual(Tenancy.objects.get(pk=made["id"]).rent_amount, Decimal("450.00"))
