from users.tests.base import UsersApiTestCase

PATHS = ["/api/users/", "/api/users/all/", "/api/users/1/"]


class UserEndpointAccessTests(UsersApiTestCase):
    def test_anonymous_gets_401(self):
        for path in PATHS:
            self.assertEqual(self.client.get(path).status_code, 401, path)

    def test_tenant_gets_403(self):
        user = self.make_user("tenant@example.com")
        self.authorize(self.sign_in(email=user.email).data["access_token"])

        for path in PATHS:
            self.assertEqual(self.client.get(path).status_code, 403, path)

    def test_admin_with_mfa_pending_gets_403(self):
        self.sign_in_as_admin(mfa_done=False)

        self.assertEqual(self.client.get("/api/users/").status_code, 403)

    def test_admin_with_mfa_done_gets_200(self):
        self.sign_in_as_admin()

        self.assertEqual(self.client.get("/api/users/").status_code, 200)

    def test_super_admin_gets_200_without_mfa(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.client.get("/api/users/").status_code, 200)


class CustomRoleAdminTests(UsersApiTestCase):
    def test_an_admin_with_only_a_custom_role_needs_mfa_then_reaches_users(self):
        self.make_role("SUPPORT", ["accounts.view"])

        self.sign_in_as_admin(mfa_done=False, roles=("SUPPORT",))
        pending = self.client.get("/api/users/")
        me = self.client.get("/api/auth/me/").data
        self.sign_in_as_admin(roles=("SUPPORT",), email="support2@example.com")
        done = self.client.get("/api/users/")

        self.assertEqual((me["mfa_status"], me["is_admin"]), ("ENROL", True))
        self.assertEqual(pending.status_code, 403)
        self.assertEqual(done.status_code, 200)

    def test_the_user_list_can_be_filtered_by_a_custom_role(self):
        self.make_role("SUPPORT", ["accounts.view"])
        self.make_admin_user("support@example.com", "SUPPORT")
        self.sign_in_as_admin(super_admin=True)

        response = self.client.get("/api/users/", {"role": "SUPPORT"})

        self.assertEqual([u["email"] for u in response.data["results"]], ["support@example.com"])
        self.assertEqual(response.data["results"][0]["role_names"], ["Support"])
