from accounts.models import AccountAccessHistory, Permission, UserPermissionBridge
from users.tests.base import UsersApiTestCase


class GrantTests(UsersApiTestCase):
    def grant(self, user_id, permission, reason="Needs it"):
        return self.post(
            f"/api/access/users/{user_id}/grants/", {"permission": permission, "reason": reason}
        )

    def revoke(self, user_id, permission):
        return self.client.delete(f"/api/access/users/{user_id}/grants/{permission}/")

    def test_grant_then_revoke_then_regrant_reuses_the_same_row(self):
        admin = self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")

        granted = self.grant(tenant.pk, "properties.create")
        revoked = self.revoke(tenant.pk, "properties.create")
        regranted = self.grant(tenant.pk, "properties.create", reason="Again")

        self.assertEqual(granted.status_code, 201)
        self.assertIn("properties.create", granted.data["effective"])
        self.assertEqual(revoked.status_code, 204)
        self.assertEqual(regranted.status_code, 201)
        self.assertEqual(UserPermissionBridge.objects.filter(user=tenant).count(), 1)
        bridge = UserPermissionBridge.objects.get(user=tenant)
        self.assertEqual(
            (bridge.is_active, bridge.reason, bridge.created_by), (True, "Again", admin)
        )
        actions = list(
            AccountAccessHistory.objects.filter(user=tenant).values_list("action", flat=True)
        )
        self.assertEqual(
            sorted(actions),
            ["ADMIN_GRANTED_PERMISSION", "ADMIN_GRANTED_PERMISSION", "ADMIN_REVOKED_PERMISSION"],
        )

    def test_a_reason_is_required(self):
        self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")

        self.assertEqual(self.grant(tenant.pk, "properties.create", reason="").status_code, 400)

    def test_you_cannot_change_your_own_grants(self):
        root = self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.grant(root.pk, "properties.create").status_code, 403)
        self.assertEqual(self.revoke(root.pk, "properties.create").status_code, 403)

    def test_you_can_only_grant_what_you_hold(self):
        self.sign_in_as_admin()
        tenant = self.make_user("ann@example.com")

        refused = self.grant(tenant.pk, "properties.create")

        self.assertEqual(refused.status_code, 403)

    def test_an_admin_who_holds_a_permission_can_grant_it_on(self):
        helper = self.make_admin_user("helper@example.com", "ADMIN")
        UserPermissionBridge.objects.create(
            user=helper, permission=Permission.objects.get(code="properties.create"), reason="Test"
        )
        tenant = self.make_user("ann@example.com")
        self.sign_in_user(helper)

        self.assertEqual(self.grant(tenant.pk, "properties.create").status_code, 201)

    def test_an_admin_cannot_grant_a_permission_they_lack_to_a_peer(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))
        peer = self.make_admin_user("peer@example.com", "LIMITED")

        self.assertEqual(self.grant(peer.pk, "accounts.delete").status_code, 403)

    def test_admin_only_permissions_are_refused_for_non_admins(self):
        self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")

        for code in ("accounts.view", "access.manage", "reviews.admin_review"):
            self.assertEqual(self.grant(tenant.pk, code).status_code, 400, code)

    def test_super_admin_can_grant_an_admin_permission_to_an_admin(self):
        self.sign_in_as_admin(super_admin=True)
        other = self.make_user("boss@example.com", role="ADMIN")

        self.assertEqual(self.grant(other.pk, "access.manage").status_code, 201)

    def test_unknown_permission_is_400_and_unknown_user_is_404(self):
        self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")

        self.assertEqual(self.grant(tenant.pk, "nope.nope").status_code, 400)
        self.assertEqual(self.grant(999999, "properties.create").status_code, 404)

    def test_user_permissions_view_separates_roles_and_grants(self):
        self.sign_in_as_admin(super_admin=True)
        tenant = self.make_user("ann@example.com")
        self.grant(tenant.pk, "properties.create")

        response = self.client.get(f"/api/access/users/{tenant.pk}/permissions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["roles"], ["Tenant"])
        self.assertIn("maintenance.report", [p["code"] for p in response.data["through_roles"]])
        self.assertEqual([g["code"] for g in response.data["grants"]], ["properties.create"])

    def test_tenant_and_admin_without_access_manage_are_refused(self):
        tenant = self.make_user("ann@example.com")
        self.authorize(self.sign_in(email=tenant.email).data["access_token"])
        self.assertEqual(self.client.get("/api/access/roles/").status_code, 403)
