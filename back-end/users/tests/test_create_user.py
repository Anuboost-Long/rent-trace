from accounts.models import AccountAccessHistory, User
from accounts.tests.base import PASSWORD
from users.tests.base import UsersApiTestCase

URL = "/api/users/"


class CreateUserTests(UsersApiTestCase):
    def test_admin_creates_a_verified_user_who_can_sign_in(self):
        admin = self.sign_in_as_admin()

        response = self.post(URL, self.new_user_payload(roles=["LANDLORD"]))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["roles"], ["LANDLORD"])
        self.assertNotIn(PASSWORD, str(response.data))
        user = User.objects.get(email_normalized="new.person@example.com")
        self.assertIsNotNone(user.email_verified_at)
        self.assertEqual(user.created_by, admin)
        history = AccountAccessHistory.objects.get(user=user)
        self.assertEqual((history.action, history.created_by), ("ADMIN_CREATED_ACCOUNT", admin))
        self.assertNotIn(PASSWORD, str(history.after_values))
        self.client.credentials()
        self.assertEqual(self.sign_in(email="new.person@example.com").status_code, 200)

    def test_super_admin_can_create_an_admin_who_must_then_enrol(self):
        self.sign_in_as_admin(super_admin=True)

        response = self.post(URL, self.new_user_payload(roles=["ADMIN"]))

        self.assertEqual(response.status_code, 201)
        self.assertFalse(
            User.objects.get(email_normalized="new.person@example.com").is_top_level_admin
        )
        self.client.credentials()
        signed_in = self.sign_in(email="new.person@example.com")
        self.assertEqual(signed_in.data["mfa_status"], "ENROL")

    def test_an_admin_who_holds_everything_can_create_an_admin(self):
        self.sign_in_as_admin()

        response = self.post(URL, self.new_user_payload(roles=["ADMIN"]))

        self.assertEqual(response.status_code, 201)

    def test_an_admin_cannot_hand_out_a_role_that_can_do_more_than_they_can(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))

        response = self.post(URL, self.new_user_payload(roles=["ADMIN"]))

        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(email_normalized="new.person@example.com").exists())

    def test_an_admin_without_access_management_cannot_create_admins(self):
        self.make_role("CLERK", ["accounts.view", "accounts.create"])
        self.sign_in_as_admin(roles=("CLERK",))
        self.make_role("OTHER", ["accounts.view"])

        self.assertEqual(self.post(URL, self.new_user_payload(roles=["OTHER"])).status_code, 403)
        self.assertEqual(self.post(URL, self.new_user_payload()).status_code, 201)

    def test_a_custom_role_can_be_assigned_on_create(self):
        self.make_role("SUPPORT", ["accounts.view"])
        self.sign_in_as_admin(super_admin=True)

        response = self.post(URL, self.new_user_payload(roles=["SUPPORT"]))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["roles"], ["SUPPORT"])
        self.assertTrue(response.data["is_admin"])

    def test_roles_cannot_mix_or_repeat_party_roles(self):
        self.sign_in_as_admin(super_admin=True)

        mixed = self.post(URL, self.new_user_payload(roles=["TENANT", "ADMIN"]))
        two_party = self.post(URL, self.new_user_payload(roles=["TENANT", "LANDLORD"]))

        self.assertEqual(mixed.status_code, 400)
        self.assertEqual(two_party.status_code, 400)

    def test_duplicate_email_is_refused(self):
        self.sign_in_as_admin()
        self.make_user("new.person@example.com")

        response = self.post(URL, self.new_user_payload())

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_weak_password_is_refused(self):
        self.sign_in_as_admin()

        response = self.post(URL, self.new_user_payload(password="short"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_unknown_role_is_refused(self):
        self.sign_in_as_admin()

        self.assertEqual(self.post(URL, self.new_user_payload(roles=["OWNER"])).status_code, 400)

    def test_tenant_cannot_create_users(self):
        user = self.make_user("tenant@example.com")
        self.authorize(self.sign_in(email=user.email).data["access_token"])

        self.assertEqual(self.post(URL, self.new_user_payload()).status_code, 403)
