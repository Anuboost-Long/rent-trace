from django.db import transaction
from rest_framework.exceptions import ValidationError

from access.services.list_role_members import ensure_admin_role
from access.services.shared import role_design
from accounts.services.shared import account_management as manage
from accounts.services.shared import role_assignment


def remove_role_member(*, actor, role_code, user_id):
    _attempt(actor, role_code, user_id)


@transaction.atomic
def _attempt(actor, role_code, user_id):
    role = role_design.find_role(role_code)
    ensure_admin_role(role)
    target = manage.find_user_for_update(user_id)
    manage.ensure_can_edit(actor, target)
    current = role_assignment.current_roles(target)
    if role.code not in current:
        return
    remaining = [code for code in current if code != role.code]
    if not remaining:
        raise ValidationError(
            "An admin needs at least one role. Pick another before removing this one."
        )
    changed = role_assignment.change_roles(actor, target, role_assignment.resolve_roles(remaining))
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_UPDATED_ACCOUNT",
        before={"roles": changed[0]},
        after={"roles": changed[1]},
        reason=f"Removed from role {role.code}",
    )
