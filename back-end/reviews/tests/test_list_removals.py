from reviews.tests.base import EvidenceApiTestCase

ADMIN = "/api/admin/removal-requests/"


class ListRemovalsTests(EvidenceApiTestCase):
    def test_each_side_and_the_admin_queue_see_the_request(self):
        record = self.record_of(self.submitted())
        request_id = self.ask_tenant_removal([record]).data["id"]

        mine = self.client.get(f"/api/tenant/tenancies/{self.tenancy['id']}/removal-requests/")
        self.as_user(self.lou)
        landlords = self.client.get(f"/api/landlord/removal-requests/?unit_id={self.unit.pk}")
        self.sign_in_as_admin(email="admin@example.com")
        queue = self.client.get(ADMIN)

        self.assertEqual([r["id"] for r in mine.data], [request_id])
        self.assertEqual([r["id"] for r in landlords.data], [request_id])
        self.assertEqual(queue.data["count"], 1)
        self.assertEqual(queue.data["results"][0]["items"][0]["title"], "Damp patch in the bedroom")

    def test_decided_ones_move_to_the_other_filters(self):
        record = self.record_of(self.submitted())
        request_id = self.ask_tenant_removal([record]).data["id"]
        self.sign_in_as_admin(email="admin@example.com")
        self.decide_removal(request_id, "approve")

        self.assertEqual(self.client.get(ADMIN).data["count"], 0)
        self.assertEqual(self.client.get(f"{ADMIN}?status=APPROVED").data["count"], 1)

    def test_other_people_cannot_see_them(self):
        record = self.record_of(self.submitted())
        self.ask_tenant_removal([record])
        self.add_tenant(self.tenancy["id"], self.sam)

        self.as_user(self.sam)
        theirs = self.client.get(f"/api/tenant/tenancies/{self.tenancy['id']}/removal-requests/")
        self.as_user(self.mia)
        other = self.client.get(f"/api/landlord/removal-requests/?unit_id={self.unit.pk}")
        self.as_user(self.lou)

        self.assertEqual(theirs.data, [])
        self.assertEqual(other.status_code, 404)
        self.assertEqual(self.client.get(ADMIN).status_code, 403)
