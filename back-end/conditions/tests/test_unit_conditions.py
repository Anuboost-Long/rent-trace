from conditions.models import ConditionRecord, ConditionVersion
from tenancies.tests.base import TenancyApiTestCase

URL = "/api/landlord/conditions/"
TENANT_URL = "/api/tenant/tenancies/"


class UnitConditionsTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.mia = self.make_user("mia@example.com", "LANDLORD", "Mia", "Cole")

    def patch(self, path, payload):
        return self.client.patch(path, payload, format="json")

    def delete(self, path):
        return self.client.delete(path)

    def note_fields(self, **extra):
        return {
            "unit_id": self.unit.pk,
            "title": "Kitchen benchtop",
            "description": "Small chip near the sink.",
            "observed_at": "2026-11-01T00:00:00Z",
            **extra,
        }

    def add_note(self, **extra):
        self.as_user(self.lou)
        response = self.post(URL, self.note_fields(**extra))
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def tenant_view(self, tenancy_id):
        self.as_user(self.tina)
        response = self.client.get(f"{TENANT_URL}{tenancy_id}/")
        self.assertEqual(response.status_code, 200, response.data)
        return response.data["unit_conditions"]

    def test_a_note_starts_hidden_and_is_saved_as_version_one(self):
        note = self.add_note()

        self.assertFalse(note["is_shown_to_tenants"])
        self.assertEqual((note["title"], note["version_no"]), ("Kitchen benchtop", 1))
        record = ConditionRecord.objects.get(pk=note["id"])
        self.assertEqual(record.record_type, "BASELINE")
        self.assertEqual(record.versions.get().source_type, "LANDLORD")

    def test_the_landlord_lists_every_note_for_their_unit(self):
        self.add_note()
        self.add_note(title="Bedroom carpet", is_shown_to_tenants=True)

        response = self.client.get(f"{URL}?unit_id={self.unit.pk}")

        self.assertEqual(
            [n["title"] for n in response.data], ["Kitchen benchtop", "Bedroom carpet"]
        )

    def test_editing_the_wording_adds_a_version_and_keeps_the_old_one(self):
        note = self.add_note()

        response = self.patch(f"{URL}{note['id']}/", {"description": "Chip filled in."})

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(
            (response.data["description"], response.data["version_no"]), ("Chip filled in.", 2)
        )
        old, new = ConditionVersion.objects.filter(condition_record_id=note["id"]).order_by(
            "version_no"
        )
        self.assertEqual(old.condition_description, "Small chip near the sink.")
        self.assertEqual(new.supersedes_version_id, old.pk)
        self.assertEqual(new.title, "Kitchen benchtop")

    def test_switching_visibility_does_not_add_a_version(self):
        note = self.add_note()

        response = self.patch(f"{URL}{note['id']}/", {"is_shown_to_tenants": True})

        self.assertTrue(response.data["is_shown_to_tenants"])
        self.assertEqual(response.data["version_no"], 1)

    def test_a_deleted_note_disappears(self):
        note = self.add_note()

        self.assertEqual(self.delete(f"{URL}{note['id']}/").status_code, 204)

        self.assertEqual(self.client.get(f"{URL}?unit_id={self.unit.pk}").data, [])
        self.assertEqual(self.patch(f"{URL}{note['id']}/", {"title": "x"}).status_code, 404)

    def test_a_title_is_required(self):
        self.as_user(self.lou)

        response = self.post(URL, self.note_fields(title=""))

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)

    def test_another_landlord_cannot_see_or_change_the_notes(self):
        note = self.add_note()
        self.as_user(self.mia)

        self.assertEqual(self.client.get(f"{URL}?unit_id={self.unit.pk}").status_code, 404)
        self.assertEqual(self.post(URL, self.note_fields()).status_code, 404)
        self.assertEqual(self.patch(f"{URL}{note['id']}/", {"title": "x"}).status_code, 404)
        self.assertEqual(self.delete(f"{URL}{note['id']}/").status_code, 404)

    def test_tenants_cannot_use_the_landlord_api(self):
        self.as_user(self.tina)

        self.assertEqual(self.client.get(f"{URL}?unit_id={self.unit.pk}").status_code, 403)

    def test_a_tenant_sees_only_the_notes_the_landlord_shows(self):
        tenancy = self.new_tenancy()
        self.add_tenant(tenancy["id"], self.tina, is_primary=True)
        self.add_note(title="Hidden scuff")
        self.add_note(title="Bedroom carpet", is_shown_to_tenants=True)

        (shown,) = self.tenant_view(tenancy["id"])

        self.assertEqual(shown["title"], "Bedroom carpet")
        self.assertEqual(set(shown), {"id", "title", "description", "observed_at"})

    def test_hiding_a_note_again_removes_it_for_the_tenant(self):
        tenancy = self.new_tenancy()
        self.add_tenant(tenancy["id"], self.tina)
        note = self.add_note(is_shown_to_tenants=True)
        self.assertEqual(len(self.tenant_view(tenancy["id"])), 1)

        self.as_user(self.lou)
        self.patch(f"{URL}{note['id']}/", {"is_shown_to_tenants": False})

        self.assertEqual(self.tenant_view(tenancy["id"]), [])

    def test_a_tenant_sees_the_newest_wording(self):
        tenancy = self.new_tenancy()
        self.add_tenant(tenancy["id"], self.tina)
        note = self.add_note(is_shown_to_tenants=True)
        self.patch(f"{URL}{note['id']}/", {"description": "Chip filled in."})

        (shown,) = self.tenant_view(tenancy["id"])

        self.assertEqual(shown["description"], "Chip filled in.")
