from dataclasses import dataclass

from django.db import transaction
from rest_framework.exceptions import ValidationError

from access.services.list_permissions import find_listed_permission
from access.services.shared.rules import ADMIN_MODULES, SELF_SERVICE_CODES
from access.services.shared.unset import UNSET
from accounts.models import Permission, RoleKind, RolePermissionBridge, UserPermissionBridge
from accounts.services.shared.account_rules import is_admin_side
from accounts.services.shared.privileges import ensure_holds


@dataclass(frozen=True)
class PermissionChanges:
    name: object = UNSET
    is_admin_only: object = UNSET
    is_active: object = UNSET


def update_permission(*, actor, code, changes):
    _attempt(actor, code, changes)
    return find_listed_permission(code)


@transaction.atomic
def _attempt(actor, code, changes):
    permission = Permission.objects.select_for_update().with_code(code).first()
    if permission is None:
        find_listed_permission(code)
    ensure_holds(actor, [code], "You can't edit a permission you don't hold yourself.")
    if changes.name is not UNSET:
        permission.name = changes.name.strip()
    if changes.is_admin_only is not UNSET:
        _change_admin_only(permission, changes.is_admin_only)
    if changes.is_active is not UNSET:
        permission.is_active = changes.is_active
    permission.save()


def _change_admin_only(permission, is_admin_only):
    if is_admin_only == permission.is_admin_only:
        return
    if not is_admin_only and (
        permission.module in ADMIN_MODULES and permission.code not in SELF_SERVICE_CODES
    ):
        raise ValidationError(
            {"is_admin_only": "Permissions in this module are always admin-only."}
        )
    if is_admin_only and _held_outside_admins(permission):
        raise ValidationError(
            {"is_admin_only": "Remove it from tenant and landlord roles and people first."}
        )
    permission.is_admin_only = is_admin_only


def _held_outside_admins(permission):
    on_party_role = (
        RolePermissionBridge.objects.active()
        .filter(permission=permission, role__kind=RoleKind.PARTY)
        .exists()
    )
    grants = UserPermissionBridge.objects.active().for_permission(permission).select_related("user")
    return on_party_role or any(not is_admin_side(grant.user) for grant in grants)
