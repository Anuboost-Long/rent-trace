from accounts.models import RolePermissionBridge
from communications.tests.base import ContactRequestApiTestCase

ADMIN_URL = "/api/admin/contact-requests/"


class AdminContactRequestsTests(ContactRequestApiTestCase):
    def sign_in_boss(self):
        return self.sign_in_as_admin(super_admin=True, email="boss@example.com")

    def request_on_another_landlords_listing(self):
        other, _ = self.listing(self.amy, suburb="Brunswick")
        self.as_user(self.sam)
        response = self.post(
            "/api/tenant/contact-requests/", {"listing_id": other["id"], "message": "Hello?"}
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def setUp(self):
        super().setUp()
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")

    def test_an_admin_sees_requests_across_landlords_with_names(self):
        mine = self.asked()
        theirs = self.request_on_another_landlords_listing()
        self.sign_in_boss()

        response = self.client.get(ADMIN_URL)

        self.assertEqual(response.status_code, 200)
        rows = {row["id"]: row for row in response.data["results"]}
        self.assertEqual(set(rows), {mine["id"], theirs["id"]})
        self.assertEqual(rows[mine["id"]]["tenant"]["first_name"], "Tina")
        self.assertEqual(rows[mine["id"]]["landlord"]["first_name"], "Lou")
        self.assertEqual(rows[theirs["id"]]["landlord"]["first_name"], "Amy")

    def test_contact_details_are_never_shown_even_once_accepted(self):
        request = self.asked()
        self.answer(request, "accept")
        self.sign_in_boss()

        body = self.client.get(f"{ADMIN_URL}{request['id']}/").data

        self.assertEqual(body["status"], "ACCEPTED")
        self.assertNotIn("tenant_contact", body)
        for person in (body["tenant"], body["landlord"]):
            self.assertEqual(set(person), {"id", "first_name", "last_name"})

    def test_the_list_filters_by_status_and_searches(self):
        mine = self.asked()
        theirs = self.request_on_another_landlords_listing()
        self.answer(mine, "decline")
        self.sign_in_boss()

        declined = self.client.get(ADMIN_URL, {"status": "DECLINED"}).data["results"]
        by_suburb = self.client.get(ADMIN_URL, {"q": "brunswick"}).data["results"]
        by_tenant = self.client.get(ADMIN_URL, {"q": "tina"}).data["results"]

        self.assertEqual([row["id"] for row in declined], [mine["id"]])
        self.assertEqual([row["id"] for row in by_suburb], [theirs["id"]])
        self.assertEqual([row["id"] for row in by_tenant], [mine["id"]])

    def test_an_unknown_request_is_not_found(self):
        self.sign_in_boss()
        self.assertEqual(self.client.get(f"{ADMIN_URL}999999/").status_code, 404)

    def test_landlords_and_tenants_are_refused(self):
        request = self.asked()
        for user in (self.lou, self.tina):
            self.as_user(user)
            self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
            self.assertEqual(self.client.get(f"{ADMIN_URL}{request['id']}/").status_code, 403)

    def test_an_admin_without_the_permission_is_refused(self):
        RolePermissionBridge.objects.filter(permission__code="contact_requests.admin_view").delete()
        self.sign_in_as_admin(email="plain@example.com")

        self.assertEqual(self.client.get(ADMIN_URL).status_code, 403)
