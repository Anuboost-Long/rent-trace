from users.tests.base import UsersApiTestCase

URL = "/api/access/grants/"


class GrantsListTests(UsersApiTestCase):
    def grant(self, user, code="properties.create", reason="Needs it"):
        return self.post(
            f"/api/access/users/{user.pk}/grants/", {"permission": code, "reason": reason}
        )

    def test_lists_active_grants_newest_first_with_who_granted_them(self):
        root = self.sign_in_as_admin(super_admin=True)
        ann = self.make_user("ann@example.com", first_name="Ann", last_name="Lee")
        bob = self.make_user("bob@example.com", first_name="Bob", last_name="Stone")
        self.grant(ann)
        self.grant(bob, "properties.update")

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["user"]["email"], "bob@example.com")
        self.assertEqual(response.data["results"][0]["granted_by"]["id"], root.pk)

    def test_filters_by_person_and_permission_and_hides_revoked(self):
        self.sign_in_as_admin(super_admin=True)
        ann = self.make_user("ann@example.com", first_name="Ann", last_name="Lee")
        bob = self.make_user("bob@example.com", first_name="Bob", last_name="Stone")
        self.grant(ann)
        self.grant(bob, "properties.update")
        self.client.delete(f"/api/access/users/{ann.pk}/grants/properties.create/")

        by_name = self.client.get(URL, {"q": "bob"})
        by_code = self.client.get(URL, {"permission": "properties.update"})
        revoked_gone = self.client.get(URL, {"permission": "properties.create"})

        self.assertEqual(by_name.data["count"], 1)
        self.assertEqual(by_code.data["count"], 1)
        self.assertEqual(revoked_gone.data["count"], 0)

    def test_needs_access_management(self):
        self.make_role("CLERK", ["accounts.view"])
        self.sign_in_as_admin(roles=("CLERK",))

        self.assertEqual(self.client.get(URL).status_code, 403)
