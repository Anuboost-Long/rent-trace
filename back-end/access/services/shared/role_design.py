from rest_framework.exceptions import NotFound, ValidationError

from accounts.models import Permission, Role, RoleKind
from accounts.services.shared.privileges import ensure_holds
from accounts.services.shared.roles import MAX_ROLE_DEPTH, role_effective_codes

HIDDEN_RECORDS = "access.view_hidden_records"


def find_role(code, *, for_update=False):
    roles = Role.objects.select_for_update() if for_update else Role.objects
    role = roles.with_code(code).first()
    if role is None:
        raise NotFound("No role with this code.")
    return role


def load_permissions(codes, kind):
    wanted = set(codes)
    permissions = list(Permission.objects.active().filter(code__in=wanted))
    unknown = wanted - {permission.code for permission in permissions}
    if unknown:
        raise ValidationError({"permissions": f"Unknown permissions: {sorted(unknown)}."})
    if HIDDEN_RECORDS in wanted:
        raise ValidationError({"permissions": "Hidden-record access can only be a personal grant."})
    admin_only = sorted(p.code for p in permissions if p.is_admin_only)
    if admin_only and kind != RoleKind.ADMIN:
        raise ValidationError({"permissions": f"Only admin roles can have: {admin_only}."})
    return permissions


def load_parent(parent_code, kind):
    if not parent_code:
        return None
    parent = Role.objects.active().with_code(parent_code).first()
    if parent is None:
        raise ValidationError({"parent": f"No active role '{parent_code}'."})
    if parent.kind != kind:
        raise ValidationError({"parent": "A role can only inherit from a role of the same kind."})
    return parent


def _levels_to_root(role):
    levels, seen, current = 0, set(), role
    while current is not None and current.pk not in seen:
        seen.add(current.pk)
        levels += 1
        current = current.parent
    return levels, seen


def _subtree_height(role):
    height, frontier = 0, [role.pk]
    while frontier:
        frontier = list(Role.objects.filter(parent_id__in=frontier).values_list("pk", flat=True))
        height += 1 if frontier else 0
    return height


def check_parent_shape(role, parent):
    """`role` is the role being edited, or None while creating."""
    if parent is None:
        return
    levels, ancestors = _levels_to_root(parent)
    if role is not None and role.pk in ancestors:
        raise ValidationError(
            {"parent": "A role can't inherit from itself or from its own children."}
        )
    own_height = _subtree_height(role) if role is not None else 0
    if levels + 1 + own_height > MAX_ROLE_DEPTH:
        raise ValidationError({"parent": f"Roles can be at most {MAX_ROLE_DEPTH} levels deep."})


def ensure_actor_holds_design(actor, direct_codes, parent):
    effective = set(direct_codes)
    if parent is not None:
        effective |= role_effective_codes(parent)
    ensure_holds(actor, effective)


def snapshot(role, direct_codes):
    return {
        "name": role.name,
        "description": role.description,
        "parent": role.parent.code if role.parent else None,
        "permissions": sorted(direct_codes),
        "is_active": role.is_active,
    }
