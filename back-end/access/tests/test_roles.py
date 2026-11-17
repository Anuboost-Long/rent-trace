from django.utils import timezone

from accounts.models import Role, RoleChangeHistory
from accounts.services.shared.permissions import permission_codes
from users.tests.base import UsersApiTestCase

URL = "/api/access/roles/"


class RoleTests(UsersApiTestCase):
    def create(self, name="Support Agent", **extra):
        return self.post(URL, {"name": name, "permissions": ["accounts.view"], **extra})

    def patch(self, code, **body):
        return self.client.patch(f"{URL}{code}/", body, format="json")

    def codes_of(self, user):
        return permission_codes(type(user).objects.get(pk=user.pk), timezone.now())

    def test_lists_roles_with_kind_parent_and_holder_counts(self):
        self.sign_in_as_admin(super_admin=True)

        roles = {role["code"]: role for role in self.client.get(URL).data}

        self.assertEqual(roles["ADMIN"]["kind"], "ADMIN")
        self.assertTrue(roles["ADMIN"]["is_system"])
        self.assertEqual(roles["TENANT"]["kind"], "PARTY")
        self.assertEqual(roles["ADMIN"]["holder_count"], 1)
        self.assertIn("accounts.view", roles["ADMIN"]["permissions"])

    def test_creates_a_custom_admin_role_and_records_history(self):
        admin = self.sign_in_as_admin(super_admin=True)

        response = self.create(description="Answers questions")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["code"], "SUPPORT_AGENT")
        self.assertEqual((response.data["kind"], response.data["is_system"]), ("ADMIN", False))
        history = RoleChangeHistory.objects.get(role__code="SUPPORT_AGENT")
        self.assertEqual((history.action, history.created_by), ("CREATED_ROLE", admin))
        self.assertEqual(self.create().data["code"], "SUPPORT_AGENT_2")

    def test_a_child_role_inherits_its_parents_permissions(self):
        self.sign_in_as_admin(super_admin=True)
        self.create("Support", permissions=["accounts.view"])
        child = self.create("Senior Support", parent="SUPPORT", permissions=["accounts.update"])
        person = self.make_admin_user("sam@example.com", "SENIOR_SUPPORT")

        self.assertEqual(child.data["inherited_permissions"], ["accounts.view"])
        self.assertTrue({"accounts.view", "accounts.update"} <= self.codes_of(person))

    def test_an_inactive_parent_stops_inheritance(self):
        self.sign_in_as_admin(super_admin=True)
        self.create("Support", permissions=["accounts.view"])
        self.create("Senior Support", parent="SUPPORT", permissions=["accounts.update"])
        person = self.make_admin_user("sam@example.com", "SENIOR_SUPPORT")
        Role.objects.filter(code="SUPPORT").update(is_active=False)

        codes = self.codes_of(person)

        self.assertIn("accounts.update", codes)
        self.assertNotIn("accounts.view", codes)

    def test_cycles_and_deep_chains_are_refused(self):
        self.sign_in_as_admin(super_admin=True)
        self.create("A", permissions=[])
        self.create("B", parent="A", permissions=[])

        cycle = self.patch("A", parent="B")
        itself = self.patch("A", parent="A")

        self.assertEqual(cycle.status_code, 400)
        self.assertEqual(itself.status_code, 400)
        previous = "B"
        for name in ("C", "D", "E"):
            self.create(name, parent=previous, permissions=[])
            previous = name
        self.assertEqual(self.create("F", parent="E", permissions=[]).status_code, 400)

    def test_you_cannot_give_a_role_permissions_you_lack(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))

        response = self.create(permissions=["accounts.delete"])

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Role.objects.filter(code="SUPPORT_AGENT").exists())

    def test_you_cannot_inherit_from_a_parent_that_can_do_more(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))

        response = self.create(parent="ADMIN", permissions=[])

        self.assertEqual(response.status_code, 403)

    def test_you_cannot_edit_a_role_that_can_do_more_than_you(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))

        self.assertEqual(self.patch("ADMIN", name="Boss").status_code, 403)

    def test_an_admin_can_edit_a_role_they_fully_hold(self):
        self.sign_in_as_admin()
        self.assertEqual(self.create("Helper", permissions=["accounts.view"]).status_code, 201)

        response = self.patch("HELPER", permissions=["accounts.view", "accounts.create"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["permissions"], ["accounts.create", "accounts.view"])
        self.assertEqual(RoleChangeHistory.objects.filter(role__code="HELPER").count(), 2)

    def test_system_roles_cannot_be_deactivated_or_given_a_parent(self):
        self.sign_in_as_admin(super_admin=True)
        self.create("Support", permissions=[])

        self.assertEqual(self.patch("ADMIN", is_active=False).status_code, 400)
        self.assertEqual(self.patch("TENANT", is_active=False).status_code, 400)
        self.assertEqual(self.patch("ADMIN", parent="SUPPORT").status_code, 400)

    def test_a_role_with_active_children_cannot_be_deactivated(self):
        self.sign_in_as_admin(super_admin=True)
        self.create("Support", permissions=[])
        self.create("Senior", parent="SUPPORT", permissions=[])

        self.assertEqual(self.patch("SUPPORT", is_active=False).status_code, 400)
        self.assertEqual(self.patch("SENIOR", is_active=False).status_code, 200)
        self.assertEqual(self.patch("SUPPORT", is_active=False).status_code, 200)

    def test_party_roles_cannot_get_admin_only_permissions_or_hidden_records(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.patch("TENANT", permissions=["accounts.view"]).status_code, 400)
        self.assertEqual(
            self.patch("ADMIN", permissions=["access.view_hidden_records"]).status_code, 400
        )

    def test_unknown_permission_parent_or_role_is_refused(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.create(permissions=["nope.nope"]).status_code, 400)
        self.assertEqual(self.create(parent="NOPE").status_code, 400)
        self.assertEqual(self.patch("NOPE", name="X").status_code, 404)

    def test_an_admin_without_access_management_cannot_use_the_endpoints(self):
        self.make_role("CLERK", ["accounts.view"])
        self.sign_in_as_admin(roles=("CLERK",))

        self.assertEqual(self.client.get(URL).status_code, 403)

    def test_lists_permissions_with_the_admin_only_flag(self):
        self.sign_in_as_admin(super_admin=True)

        permissions = {p["code"]: p for p in self.client.get("/api/access/permissions/").data}

        self.assertTrue(permissions["accounts.view"]["is_admin_only"])
        self.assertFalse(permissions["properties.create"]["is_admin_only"])
