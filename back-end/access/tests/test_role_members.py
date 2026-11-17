from accounts.models import AccountAccessHistory
from users.tests.base import UsersApiTestCase


class RoleMemberTests(UsersApiTestCase):
    def members_url(self, code):
        return f"/api/access/roles/{code}/members/"

    def test_lists_the_people_in_a_role(self):
        self.make_role("SUPPORT", ["accounts.view"])
        self.make_admin_user("sam@example.com", "SUPPORT")
        self.sign_in_as_admin(super_admin=True)

        response = self.client.get(self.members_url("SUPPORT"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([m["email"] for m in response.data["results"]], ["sam@example.com"])
        self.assertEqual(response.data["results"][0]["role_names"], ["Support"])

    def test_adds_and_removes_a_member_keeping_their_other_roles(self):
        self.make_role("SUPPORT", ["accounts.view"])
        self.make_role("FINANCE", ["accounts.update"])
        sam = self.make_admin_user("sam@example.com", "SUPPORT")
        self.sign_in_as_admin(super_admin=True)

        added = self.post(self.members_url("FINANCE"), {"user_id": sam.pk})
        both = self.client.get(self.members_url("FINANCE")).data["results"][0]["role_names"]
        removed = self.client.delete(f"{self.members_url('FINANCE')}{sam.pk}/")

        self.assertEqual(added.status_code, 204)
        self.assertEqual(sorted(both), ["Finance", "Support"])
        self.assertEqual(removed.status_code, 204)
        self.assertEqual(self.client.get(self.members_url("FINANCE")).data["count"], 0)
        self.assertEqual(self.client.get(self.members_url("SUPPORT")).data["count"], 1)
        self.assertEqual(
            AccountAccessHistory.objects.filter(user=sam, action="ADMIN_UPDATED_ACCOUNT").count(), 2
        )

    def test_the_last_role_cannot_be_removed(self):
        self.make_role("SUPPORT", ["accounts.view"])
        sam = self.make_admin_user("sam@example.com", "SUPPORT")
        self.sign_in_as_admin(super_admin=True)

        response = self.client.delete(f"{self.members_url('SUPPORT')}{sam.pk}/")

        self.assertEqual(response.status_code, 400)

    def test_party_roles_and_party_people_are_handled_on_the_users_page(self):
        self.make_role("SUPPORT", ["accounts.view"])
        tenant = self.make_user("ann@example.com")
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(
            self.post(self.members_url("TENANT"), {"user_id": tenant.pk}).status_code, 400
        )
        self.assertEqual(
            self.post(self.members_url("SUPPORT"), {"user_id": tenant.pk}).status_code, 400
        )

    def test_you_cannot_add_someone_to_a_role_that_can_do_more_than_you(self):
        self.limited_admin_role()
        sam = self.make_admin_user("sam@example.com", "LIMITED")
        self.sign_in_as_admin(roles=("LIMITED",), email="lim@example.com")

        response = self.post(self.members_url("ADMIN"), {"user_id": sam.pk})

        self.assertEqual(response.status_code, 403)

    def test_you_cannot_change_your_own_membership(self):
        self.make_role("SUPPORT", ["accounts.view"])
        me = self.sign_in_as_admin(super_admin=True)

        self.assertEqual(
            self.post(self.members_url("SUPPORT"), {"user_id": me.pk}).status_code, 403
        )
