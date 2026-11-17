from communications.tests.base import TENANT_URL, ContactRequestApiTestCase


class MyContactRequestsTests(ContactRequestApiTestCase):
    def test_a_tenant_lists_only_their_own_requests(self):
        mine = self.asked()
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Poe")
        self.asked(sam)
        self.as_user(self.tina)

        listed = self.client.get(TENANT_URL).data

        self.assertEqual([r["id"] for r in listed["results"]], [mine["id"]])
        self.assertEqual(self.client.get(TENANT_URL, {"status": "ACCEPTED"}).data["count"], 0)

    def test_someone_elses_request_is_not_found(self):
        sam = self.make_user("sam@example.com", "TENANT", "Sam", "Poe")
        theirs = self.asked(sam)
        self.as_user(self.tina)

        self.assertEqual(self.client.get(f"{TENANT_URL}{theirs['id']}/").status_code, 404)
        self.assertEqual(self.post(f"{TENANT_URL}{theirs['id']}/cancel/").status_code, 404)

    def test_a_waiting_request_can_be_cancelled_then_asked_again(self):
        request = self.asked()

        cancelled = self.post(f"{TENANT_URL}{request['id']}/cancel/")

        self.assertEqual(cancelled.data["status"], "CANCELLED")
        self.assertEqual(self.ask().status_code, 201)

    def test_an_answered_request_cannot_be_cancelled(self):
        request = self.asked()
        self.answer(request, "accept")
        self.as_user(self.tina)

        self.assertEqual(self.post(f"{TENANT_URL}{request['id']}/cancel/").status_code, 400)
        self.assertEqual(self.stored(request).status, "ACCEPTED")

    def test_landlords_cannot_use_the_tenant_api(self):
        self.as_user(self.lou)

        self.assertEqual(self.client.get(TENANT_URL).status_code, 403)
