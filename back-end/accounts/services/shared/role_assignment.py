from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import Role, RoleKind, UserRoleBridge
from accounts.services.shared.permissions import has_permission
from accounts.services.shared.privileges import ensure_holds
from accounts.services.shared.roles import role_effective_codes

MANAGE_ACCESS = "access.manage"


def resolve_roles(role_codes):
    codes = list(dict.fromkeys(role_codes))
    roles = list(Role.objects.active().filter(code__in=codes))
    unknown = set(codes) - {role.code for role in roles}
    if unknown:
        raise ValidationError({"roles": f"Unknown roles: {sorted(unknown)}."})
    if not roles:
        raise ValidationError({"roles": "Pick at least one role."})
    kinds = {role.kind for role in roles}
    if len(kinds) > 1:
        raise ValidationError({"roles": "A person is either a tenant or landlord, or an admin."})
    if kinds == {RoleKind.PARTY} and len(roles) > 1:
        raise ValidationError({"roles": "Pick either Tenant or Landlord."})
    return roles


def current_roles(user):
    bridges = user.role_bridges.active().select_related("role")
    return {bridge.role.code: bridge.role for bridge in bridges}


def change_roles(actor, target, roles):
    """Make `roles` the target's active roles. Returns (before, after) codes, or None if same."""
    current = current_roles(target)
    wanted = {role.code: role for role in roles}
    if set(current) == set(wanted):
        return None
    if actor.pk == target.pk:
        raise PermissionDenied("You can't change your own roles.")
    _ensure_may_change(actor, [*current.values(), *wanted.values()])

    existing = {bridge.role_id: bridge for bridge in target.role_bridges.all()}
    for bridge in existing.values():
        bridge.is_active = bridge.role.code in wanted
        bridge.updated_by = actor
        bridge.row_version += 1
        bridge.save()
    for role in roles:
        if role.pk not in existing:
            UserRoleBridge.objects.create(user=target, role=role, created_by=actor)
    return sorted(current), sorted(wanted)


def _ensure_may_change(actor, involved_roles):
    admin_roles = {role.code: role for role in involved_roles if role.kind == RoleKind.ADMIN}
    if not admin_roles:
        return
    if not has_permission(actor, MANAGE_ACCESS, timezone.now()):
        raise PermissionDenied("You need access management to change admin roles.")
    for role in admin_roles.values():
        ensure_holds(actor, role_effective_codes(role))
