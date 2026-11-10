from accounts.models import AccountAccessHistory, User
from users.tests.base import UsersApiTestCase


class UpdateUserTests(UsersApiTestCase):
    def patch(self, user_id, **body):
        return self.client.patch(f"/api/users/{user_id}/", body, format="json")

    def test_updates_names_and_phone_and_records_the_change(self):
        admin = self.sign_in_as_admin()
        user = self.make_user("ann@example.com")

        response = self.patch(user.pk, first_name="Anna", phone_number="012 345 678")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Anna")
        self.assertEqual(response.data["phone_number"], "012 345 678")
        user.refresh_from_db()
        self.assertEqual((user.updated_by, user.row_version), (admin, 2))
        history = AccountAccessHistory.objects.get(user=user, action="ADMIN_UPDATED_ACCOUNT")
        self.assertEqual(history.created_by, admin)
        self.assertEqual(history.after_values["first_name"], "Anna")

    def test_blank_phone_clears_it(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")
        self.patch(user.pk, phone_number="012")

        response = self.patch(user.pk, phone_number="")

        self.assertIsNone(response.data["phone_number"])

    def test_nothing_changed_writes_no_history(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")

        self.patch(user.pk, first_name=user.first_name)

        self.assertFalse(
            AccountAccessHistory.objects.filter(action="ADMIN_UPDATED_ACCOUNT").exists()
        )

    def test_changes_a_role(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")

        response = self.patch(user.pk, roles=["LANDLORD"])

        self.assertEqual(response.data["roles"], ["LANDLORD"])

    def test_email_cannot_be_changed(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")

        self.patch(user.pk, email="other@example.com")

        user.refresh_from_db()
        self.assertEqual(user.email, "ann@example.com")

    def test_a_peer_admin_can_edit_another_admin(self):
        self.sign_in_as_admin()
        other_admin = self.make_admin_user("boss@example.com", "ADMIN")

        self.assertEqual(self.patch(other_admin.pk, first_name="Bo").status_code, 200)

    def test_an_admin_cannot_edit_or_promote_to_something_more_powerful_than_themselves(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))
        full_admin = self.make_admin_user("boss@example.com", "ADMIN")
        tenant = self.make_user("ann@example.com")

        self.assertEqual(self.patch(full_admin.pk, first_name="X").status_code, 403)
        self.assertEqual(self.patch(tenant.pk, roles=["ADMIN"]).status_code, 403)

    def test_an_admin_holds_several_roles_and_gets_the_union(self):
        self.make_role("VIEWER", ["accounts.view"])
        self.make_role("CREATOR", ["accounts.create"])
        self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")

        response = self.patch(tenant.pk, roles=["VIEWER", "CREATOR"])

        self.assertEqual(sorted(response.data["roles"]), ["CREATOR", "VIEWER"])
        self.client.credentials()
        self.authorize(self.sign_in(email="ann@example.com").data["access_token"])
        me = self.client.get("/api/auth/me/").data
        self.assertEqual(me["mfa_status"], "ENROL")
        self.assertTrue(me["is_admin"])
        self.assertTrue({"accounts.view", "accounts.create"} <= set(me["permissions"]))

    def test_super_admin_can_promote_but_not_change_their_own_roles(self):
        root = self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")

        promoted = self.patch(tenant.pk, roles=["ADMIN"])
        own = self.patch(root.pk, roles=["TENANT"])

        self.assertEqual(promoted.data["roles"], ["ADMIN"])
        self.assertEqual(own.status_code, 403)
        self.assertFalse(User.objects.get(pk=tenant.pk).is_top_level_admin)

    def test_missing_user_is_404(self):
        self.sign_in_as_admin()

        self.assertEqual(self.patch(999999, first_name="X").status_code, 404)
