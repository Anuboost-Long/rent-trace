import re
import uuid

from django.db import transaction
from rest_framework.exceptions import ValidationError

from access.services.list_roles import find_listed_role
from access.services.shared import role_design
from accounts.models import Role, RoleChangeHistory, RoleKind, RolePermissionBridge

MAX_CODE_LENGTH = 30


def create_role(*, actor, name, description, parent_code, permission_codes, reason=None):
    code = _attempt(actor, name.strip(), description, parent_code, permission_codes, reason)
    return find_listed_role(code)


def _code_for(name):
    base = re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")[:MAX_CODE_LENGTH]
    if not base:
        raise ValidationError({"name": "Use letters or numbers in the role name."})
    code, number = base, 1
    while Role.objects.with_code(code).exists():
        number += 1
        suffix = f"_{number}"
        code = f"{base[: MAX_CODE_LENGTH - len(suffix)]}{suffix}"
    return code


@transaction.atomic
def _attempt(actor, name, description, parent_code, permission_codes, reason):
    parent = role_design.load_parent(parent_code, RoleKind.ADMIN)
    permissions = role_design.load_permissions(permission_codes, RoleKind.ADMIN)
    role_design.check_parent_shape(None, parent)
    role_design.ensure_actor_holds_design(actor, {p.code for p in permissions}, parent)

    role = Role.objects.create(
        code=_code_for(name),
        name=name,
        description=description or None,
        kind=RoleKind.ADMIN,
        parent=parent,
    )
    RolePermissionBridge.objects.bulk_create(
        RolePermissionBridge(role=role, permission=permission, created_by=actor)
        for permission in permissions
    )
    RoleChangeHistory.objects.create(
        role=role,
        action="CREATED_ROLE",
        before_values={},
        after_values=role_design.snapshot(role, {p.code for p in permissions}),
        reason=reason or f"Created by admin {actor.pk}",
        correlation_id=uuid.uuid4(),
        created_by=actor,
    )
    return role.code
