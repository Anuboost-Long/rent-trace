from accounts.models import Permission, UserPermissionBridge
from users.tests.base import UsersApiTestCase

URL = "/api/access/permissions/"


class PermissionCatalogueTests(UsersApiTestCase):
    def create(self, code="reports.export", name="Export reports", **extra):
        return self.post(URL, {"code": code, "name": name, **extra})

    def patch(self, code, **body):
        return self.client.patch(f"{URL}{code}/", body, format="json")

    def test_creates_a_permission_with_its_module(self):
        self.sign_in_as_admin()

        response = self.create()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            (response.data["module"], response.data["is_admin_only"]), ("reports", False)
        )
        self.assertEqual(response.data["roles"], [])

    def test_admin_modules_are_always_admin_only(self):
        self.sign_in_as_admin()

        response = self.create(code="accounts.export", name="Export accounts")

        self.assertTrue(response.data["is_admin_only"])

    def test_code_must_look_like_module_dot_action_and_be_unique(self):
        self.sign_in_as_admin()

        self.assertEqual(self.create(code="Reports Export").status_code, 400)
        self.assertEqual(self.create(code="export").status_code, 400)
        self.create()
        self.assertEqual(self.create().status_code, 400)

    def test_edits_name_and_deactivates_but_only_if_you_hold_it(self):
        self.sign_in_as_admin(super_admin=True)
        self.create()

        renamed = self.patch("reports.export", name="Download reports")
        off = self.patch("reports.export", is_active=False)

        self.assertEqual(renamed.data["name"], "Download reports")
        self.assertEqual(off.status_code, 200)
        self.assertFalse(Permission.objects.get(code="reports.export").is_active)

    def test_you_cannot_edit_a_permission_you_lack(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))

        self.assertEqual(self.patch("accounts.delete", name="X").status_code, 403)

    def test_admin_only_cannot_be_dropped_for_admin_modules_or_set_while_non_admins_hold_it(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.patch("accounts.view", is_admin_only=False).status_code, 400)
        self.assertEqual(self.patch("maintenance.report", is_admin_only=True).status_code, 400)

    def test_unknown_permission_is_404(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.patch("nope.nope", name="X").status_code, 404)

    def test_lists_who_holds_a_permission(self):
        root = self.sign_in_as_admin(super_admin=True)
        self.create()
        tenant = self.make_user("ann@example.com")
        UserPermissionBridge.objects.create(
            user=tenant,
            permission=Permission.objects.get(code="reports.export"),
            reason="Needs reports",
            created_by=root,
        )
        self.make_role("ANALYST", ["reports.export"])
        self.make_role("SENIOR_ANALYST", parent=Role_by_code("ANALYST"))
        self.make_admin_user("sam@example.com", "SENIOR_ANALYST")

        data = self.client.get(f"{URL}reports.export/holders/").data

        roles = {role["code"]: role["inherited"] for role in data["roles"]}
        self.assertEqual(roles, {"ANALYST": False, "SENIOR_ANALYST": True})
        self.assertEqual(data["people_through_roles"], 1)
        self.assertEqual(data["grants"][0]["user"]["email"], "ann@example.com")
        self.assertEqual(data["grants"][0]["granted_by"]["id"], root.pk)


def Role_by_code(code):
    from accounts.models import Role

    return Role.objects.get(code=code)
