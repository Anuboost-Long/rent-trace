from reviews.tests.base import EvidenceApiTestCase

ADMIN = "/api/admin/condition-corrections/"


class ListCorrectionsTests(EvidenceApiTestCase):
    def test_each_side_and_the_admin_queue_see_the_request(self):
        note = self.shown_note()
        request_id = self.ask_tenant_correction(note["id"]).data["id"]

        mine = self.client.get(f"/api/tenant/tenancies/{self.tenancy['id']}/condition-corrections/")
        self.as_user(self.lou)
        landlords = self.client.get(f"/api/landlord/condition-corrections/?unit_id={self.unit.pk}")
        self.sign_in_as_admin(email="admin@example.com")
        queue = self.client.get(ADMIN)

        self.assertEqual([r["id"] for r in mine.data], [request_id])
        self.assertEqual([r["id"] for r in landlords.data], [request_id])
        self.assertEqual(queue.data["count"], 1)
        self.assertEqual(queue.data["results"][0]["place"], queue.data["results"][0]["place"])

    def test_an_admin_opens_one_correction_by_id_and_others_cannot(self):
        note = self.shown_note()
        request_id = self.ask_tenant_correction(note["id"]).data["id"]
        self.sign_in_as_admin(email="admin@example.com")

        opened = self.client.get(f"{ADMIN}{request_id}/")
        missing = self.client.get(f"{ADMIN}999999/")
        self.as_user(self.lou)

        self.assertEqual(opened.status_code, 200, opened.data)
        self.assertEqual(opened.data["id"], request_id)
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(self.client.get(f"{ADMIN}{request_id}/").status_code, 403)

    def test_decided_ones_move_to_the_other_filters(self):
        note = self.shown_note()
        request_id = self.ask_tenant_correction(note["id"]).data["id"]
        self.sign_in_as_admin(email="admin@example.com")
        self.decide_correction(request_id, "approve")

        self.assertEqual(self.client.get(ADMIN).data["count"], 0)
        self.assertEqual(self.client.get(f"{ADMIN}?status=APPROVED").data["count"], 1)

    def test_another_tenants_and_other_landlords_lists_are_empty_or_404(self):
        note = self.shown_note()
        self.ask_tenant_correction(note["id"])
        self.add_tenant(self.tenancy["id"], self.sam)

        self.as_user(self.sam)
        theirs = self.client.get(
            f"/api/tenant/tenancies/{self.tenancy['id']}/condition-corrections/"
        )
        self.as_user(self.mia)
        other = self.client.get(f"/api/landlord/condition-corrections/?unit_id={self.unit.pk}")

        self.assertEqual(theirs.data, [])
        self.assertEqual(other.status_code, 404)
        self.as_user(self.lou)
        self.assertEqual(self.client.get(ADMIN).status_code, 403)
