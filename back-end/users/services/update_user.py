from dataclasses import dataclass

from django.db import transaction

from accounts.services.shared import account_management as manage
from accounts.services.shared import role_assignment
from users.services.get_user import get_user

UNSET = object()


@dataclass(frozen=True)
class UserChanges:
    first_name: object = UNSET
    last_name: object = UNSET
    phone_number: object = UNSET
    role_codes: object = UNSET


def update_user(*, actor, user_id, changes):
    roles = (
        role_assignment.resolve_roles(changes.role_codes)
        if changes.role_codes is not UNSET
        else None
    )
    _apply(actor, user_id, changes, roles)
    return get_user(user_id=user_id)


@transaction.atomic
def _apply(actor, user_id, changes, roles):
    now = manage.now()
    target = manage.find_user_for_update(user_id)
    manage.ensure_can_edit(actor, target)
    before, after = {}, {}

    for field, new_value in _profile_changes(changes).items():
        old_value = getattr(target, field)
        if new_value != old_value:
            before[field], after[field] = old_value, new_value
            setattr(target, field, new_value)

    if roles is not None:
        changed = role_assignment.change_roles(actor, target, roles)
        if changed:
            before["roles"], after["roles"] = changed

    if not after:
        return
    manage.save_change(actor, target, now)
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_UPDATED_ACCOUNT",
        before=before,
        after=after,
        reason=None,
    )


def _profile_changes(changes):
    fields = {
        "first_name": changes.first_name,
        "last_name": changes.last_name,
        "phone_number": changes.phone_number,
    }
    return {field: value for field, value in fields.items() if value is not UNSET}
