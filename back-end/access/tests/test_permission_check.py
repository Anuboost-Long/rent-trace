from django.utils import timezone

from accounts.models import (
    AccessPolicy,
    Permission,
    Role,
    RolePermissionBridge,
    User,
    UserPermissionBridge,
)
from accounts.services.shared.permissions import HIDDEN_RECORDS, permission_codes
from users.tests.base import UsersApiTestCase


class PermissionCheckTests(UsersApiTestCase):
    def codes(self, user):
        return permission_codes(User.objects.get(pk=user.pk), timezone.now())

    def test_seeding_gives_the_admin_role_its_permissions(self):
        admin = self.make_user("boss@example.com", role="ADMIN")
        tenant = self.make_user("ann@example.com")

        self.assertIn("accounts.view", self.codes(admin))
        self.assertNotIn("accounts.view", self.codes(tenant))
        self.assertIn("maintenance.report", self.codes(tenant))

    def test_switching_off_a_role_permission_blocks_a_regular_admin_but_not_the_super_admin(self):
        self.sign_in_as_admin()
        self.assertEqual(self.client.get("/api/users/").status_code, 200)
        RolePermissionBridge.objects.filter(
            role__code="ADMIN", permission__code="accounts.view"
        ).update(is_active=False)

        self.assertEqual(self.client.get("/api/users/").status_code, 403)
        self.client.credentials()
        self.sign_in_as_admin(super_admin=True, email="root@example.com")
        self.assertEqual(self.client.get("/api/users/").status_code, 200)

    def test_inactive_permission_or_role_grants_nothing(self):
        admin = self.make_user("boss@example.com", role="ADMIN")
        Permission.objects.filter(code="accounts.view").update(is_active=False)
        self.assertNotIn("accounts.view", self.codes(admin))

        Permission.objects.filter(code="accounts.view").update(is_active=True)
        Role.objects.filter(code="ADMIN").update(is_active=False)
        self.assertNotIn("accounts.view", self.codes(admin))

    def test_an_individual_grant_adds_a_permission(self):
        tenant = self.make_user("ann@example.com")
        UserPermissionBridge.objects.create(
            user=tenant,
            permission=Permission.objects.get(code="properties.create"),
            reason="Owns a flat too",
        )

        self.assertIn("properties.create", self.codes(tenant))

    def test_suspended_user_has_no_permissions(self):
        tenant = self.make_user("ann@example.com")
        User.objects.filter(pk=tenant.pk).update(account_status="SUSPENDED")

        self.assertEqual(self.codes(tenant), set())

    def test_super_admin_has_every_code_except_hidden_records(self):
        root = self.make_user("root@example.com", role="ADMIN")
        User.objects.filter(pk=root.pk).update(is_top_level_admin=True)

        codes = self.codes(root)

        self.assertIn("reviews.admin_review", codes)
        self.assertNotIn(HIDDEN_RECORDS, codes)

    def test_hidden_records_needs_policy_top_level_admin_and_an_individual_grant(self):
        root = self.make_user("root@example.com", role="ADMIN")
        User.objects.filter(pk=root.pk).update(is_top_level_admin=True)
        grant = UserPermissionBridge.objects.create(
            user=root, permission=Permission.objects.get(code=HIDDEN_RECORDS), reason="Audit"
        )
        self.assertNotIn(HIDDEN_RECORDS, self.codes(root))

        AccessPolicy.objects.filter(id=1).update(hidden_records_mode="EXPLICIT_TOP_LEVEL")
        self.assertIn(HIDDEN_RECORDS, self.codes(root))

        grant.delete()
        self.assertNotIn(HIDDEN_RECORDS, self.codes(root))

    def test_a_regular_admin_never_gets_hidden_records(self):
        admin = self.make_user("boss@example.com", role="ADMIN")
        UserPermissionBridge.objects.create(
            user=admin, permission=Permission.objects.get(code=HIDDEN_RECORDS), reason="Audit"
        )
        AccessPolicy.objects.filter(id=1).update(hidden_records_mode="EXPLICIT_TOP_LEVEL")

        self.assertNotIn(HIDDEN_RECORDS, self.codes(admin))

    def test_me_lists_the_effective_permissions(self):
        self.sign_in_as_admin(super_admin=True)

        permissions = self.client.get("/api/auth/me/").data["permissions"]

        self.assertIn("accounts.view", permissions)
        self.assertNotIn(HIDDEN_RECORDS, permissions)
