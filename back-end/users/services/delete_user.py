from django.db import transaction

from accounts.services.shared import account_management as manage
from accounts.services.shared.sessions import revoke_sessions


@transaction.atomic
def delete_user(*, actor, user_id, reason=None):
    now = manage.now()
    target = manage.find_user_for_update(user_id)
    manage.ensure_can_remove(actor, target, "delete")
    target.deleted_at = now
    target.deleted_by = actor
    manage.save_change(actor, target, now)
    revoke_sessions(target, now)
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_DELETED_ACCOUNT",
        before={"deleted": False},
        after={"deleted": True},
        reason=reason,
    )
