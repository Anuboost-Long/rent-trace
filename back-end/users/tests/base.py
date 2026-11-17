from django.utils import timezone

from accounts.models import (
    AuthSession,
    Permission,
    Role,
    RolePermissionBridge,
    User,
    UserMfa,
    UserRoleBridge,
)
from accounts.services.shared.account_rules import assign_role
from accounts.tests.base import PASSWORD, AuthApiTestCase

ADMIN_EMAIL = "admin@example.com"


class UsersApiTestCase(AuthApiTestCase):
    def make_role(self, code, permission_codes=(), parent=None, kind="ADMIN"):
        role = Role.objects.create(code=code, name=code.title(), kind=kind, parent=parent)
        for permission in Permission.objects.filter(code__in=permission_codes):
            RolePermissionBridge.objects.create(role=role, permission=permission)
        return role

    def give_roles(self, user, *role_codes):
        user.role_bridges.update(is_active=False)
        for code in role_codes:
            bridge, _ = UserRoleBridge.objects.get_or_create(
                user=user, role=Role.objects.get(code=code)
            )
            bridge.is_active = True
            bridge.save()

    def sign_in_as_admin(
        self, *, super_admin=False, mfa_done=True, email=ADMIN_EMAIL, roles=("ADMIN",)
    ):
        admin = self.verified_user(email=email)
        self.give_roles(admin, *roles)
        if super_admin:
            User.objects.filter(pk=admin.pk).update(is_top_level_admin=True)
        elif mfa_done:
            UserMfa.objects.create(
                user=admin, secret_encrypted="not-used-here", confirmed_at=timezone.now()
            )
        response = self.sign_in(email=email)
        if mfa_done and not super_admin:
            AuthSession.objects.filter(user=admin).update(mfa_verified_at=timezone.now())
        self.authorize(response.data["access_token"])
        return admin

    def sign_in_user(self, user, *, mfa_done=True):
        if mfa_done and not user.is_top_level_admin:
            UserMfa.objects.get_or_create(
                user=user, defaults={"secret_encrypted": "x", "confirmed_at": timezone.now()}
            )
        response = self.sign_in(email=user.email)
        if mfa_done:
            AuthSession.objects.filter(user=user).update(mfa_verified_at=timezone.now())
        self.client.credentials()
        self.authorize(response.data["access_token"])

    def make_user(self, email, role="TENANT", first_name="Ann", last_name="Lee"):
        user = self.verified_user(email=email)
        assign_role(user, role)
        User.objects.filter(pk=user.pk).update(first_name=first_name, last_name=last_name)
        return user

    def make_admin_user(self, email, *role_codes):
        user = self.verified_user(email=email)
        self.give_roles(user, *role_codes)
        return user

    def limited_admin_role(self, code="LIMITED", without=("accounts.delete",), parent=None):
        admin_codes = set(
            Permission.objects.filter(role_bridges__role__code="ADMIN").values_list(
                "code", flat=True
            )
        )
        return self.make_role(code, admin_codes - set(without), parent=parent)

    def new_user_payload(self, **extra):
        return {
            "email": "new.person@example.com",
            "password": PASSWORD,
            "first_name": "Nia",
            "last_name": "Park",
            "roles": ["TENANT"],
            **extra,
        }
