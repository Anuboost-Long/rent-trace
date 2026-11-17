import uuid
from dataclasses import dataclass

from django.db import transaction
from rest_framework.exceptions import ValidationError

from access.services.list_roles import find_listed_role
from access.services.shared import role_design
from access.services.shared.unset import UNSET
from accounts.models import Permission, RoleChangeHistory, RolePermissionBridge
from accounts.services.shared.privileges import ensure_holds
from accounts.services.shared.roles import role_effective_codes


@dataclass(frozen=True)
class RoleChanges:
    name: object = UNSET
    description: object = UNSET
    parent_code: object = UNSET
    permission_codes: object = UNSET
    is_active: object = UNSET


def update_role(*, actor, role_code, changes, reason=None):
    _attempt(actor, role_code, changes, reason)
    return find_listed_role(role_code)


def _direct_codes(role):
    return set(
        RolePermissionBridge.objects.active()
        .filter(role=role)
        .values_list("permission__code", flat=True)
    )


@transaction.atomic
def _attempt(actor, role_code, changes, reason):
    role = role_design.find_role(role_code, for_update=True)
    ensure_holds(
        actor, role_effective_codes(role), "You can't edit a role that can do more than you can."
    )
    direct_before = _direct_codes(role)
    before = role_design.snapshot(role, direct_before)

    parent, direct_after = _apply_changes(role, changes, direct_before)

    role_design.ensure_actor_holds_design(actor, direct_after, parent)
    role.parent = parent
    _store_permissions(actor, role, direct_after)
    role.save()

    after = role_design.snapshot(role, direct_after)
    if after == before:
        return
    RoleChangeHistory.objects.create(
        role=role,
        action="UPDATED_ROLE",
        before_values=before,
        after_values=after,
        reason=reason or f"Updated by admin {actor.pk}",
        correlation_id=uuid.uuid4(),
        created_by=actor,
    )


def _apply_changes(role, changes, direct_before):
    if changes.name is not UNSET:
        role.name = changes.name.strip()
    if changes.description is not UNSET:
        role.description = changes.description or None
    parent = role.parent
    if changes.parent_code is not UNSET:
        parent = _change_parent(role, changes.parent_code)
    direct_after = direct_before
    if changes.permission_codes is not UNSET:
        permissions = role_design.load_permissions(changes.permission_codes, role.kind)
        direct_after = {permission.code for permission in permissions}
    if changes.is_active is not UNSET:
        _change_active(role, changes.is_active)
    return parent, direct_after


def _change_parent(role, parent_code):
    if role.is_system:
        raise ValidationError({"parent": "A built-in role can't inherit from another role."})
    parent = role_design.load_parent(parent_code, role.kind)
    role_design.check_parent_shape(role, parent)
    return parent


def _change_active(role, is_active):
    if role.is_active == is_active:
        return
    if role.is_system and not is_active:
        raise ValidationError({"is_active": "A built-in role can't be deactivated."})
    if not is_active and role.children.filter(is_active=True).exists():
        raise ValidationError(
            {"is_active": "Other roles inherit from this one. Change them first."}
        )
    role.is_active = is_active


def _store_permissions(actor, role, wanted_codes):
    existing = {}
    for bridge in RolePermissionBridge.objects.filter(role=role).select_related("permission"):
        existing[bridge.permission.code] = bridge
        should_be_active = bridge.permission.code in wanted_codes
        if bridge.is_active != should_be_active:
            bridge.is_active = should_be_active
            bridge.updated_by = actor
            bridge.row_version += 1
            bridge.save()
    missing = Permission.objects.active().filter(code__in=wanted_codes - set(existing))
    RolePermissionBridge.objects.bulk_create(
        RolePermissionBridge(role=role, permission=permission, created_by=actor)
        for permission in missing
    )
