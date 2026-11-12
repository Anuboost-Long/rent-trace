from properties.models import PropertyUnit
from tenancies.models import Tenancy
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TenancyApiTestCase


class CreateTenancyTests(TenancyApiTestCase):
    def test_a_landlord_creates_a_draft_tenancy_on_their_unit(self):
        self.as_user(self.lou)

        response = self.post(
            LANDLORD_URL,
            {"property_unit_id": self.unit.pk, "start_date": "2026-12-01", "notes": " "},
        )

        self.assertEqual(response.status_code, 201, response.data)
        made = Tenancy.objects.get()
        self.assertEqual((made.status, made.tenancy_type), ("DRAFT", "WHOLE_UNIT"))
        self.assertEqual(made.created_by, self.lou)
        self.assertTrue(made.reference_no.startswith("T-"))
        self.assertEqual(response.data["unit"]["id"], self.unit.pk)
        self.assertEqual((response.data["tenants"], response.data["invitations"]), ([], []))

    def test_end_date_must_be_after_start_date(self):
        self.as_user(self.lou)

        response = self.post(
            LANDLORD_URL,
            {
                "property_unit_id": self.unit.pk,
                "start_date": "2026-12-01",
                "end_date": "2026-12-01",
            },
        )

        self.assertIn("end_date", response.data)
        self.assertFalse(Tenancy.objects.exists())

    def test_a_landlord_cannot_use_someone_elses_unit(self):
        self.as_user(self.amy)

        response = self.post(
            LANDLORD_URL, {"property_unit_id": self.unit.pk, "start_date": "2026-12-01"}
        )

        self.assertIn("property_unit_id", response.data)
        self.assertFalse(Tenancy.objects.exists())

    def test_a_removed_unit_cannot_be_used(self):
        PropertyUnit.objects.update(deleted_at=self.lou.created_at)
        self.as_user(self.lou)

        response = self.post(
            LANDLORD_URL, {"property_unit_id": self.unit.pk, "start_date": "2026-12-01"}
        )

        self.assertIn("property_unit_id", response.data)

    def test_a_landlord_only_reads_their_own_tenancies(self):
        made = self.new_tenancy()

        self.assertEqual(self.client.get(f"{LANDLORD_URL}{made['id']}/").status_code, 200)
        self.as_user(self.amy)
        self.assertEqual(self.client.get(f"{LANDLORD_URL}{made['id']}/").status_code, 404)

    def test_tenants_cannot_use_the_landlord_api(self):
        self.as_user(self.tina)

        self.assertEqual(
            self.post(
                LANDLORD_URL, {"property_unit_id": self.unit.pk, "start_date": "2026-12-01"}
            ).status_code,
            403,
        )

    def test_an_admin_creates_and_reads_any_tenancy(self):
        self.sign_in_as_admin()

        created = self.post(
            ADMIN_URL, {"property_unit_id": self.unit.pk, "start_date": "2026-12-01"}
        )

        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(self.client.get(f"{ADMIN_URL}{created.data['id']}/").status_code, 200)

    def test_signing_in_is_required(self):
        self.client.credentials()
        self.assertEqual(self.post(LANDLORD_URL, {}).status_code, 401)
