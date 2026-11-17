from django.db import transaction

from accounts.models import AccountStatus
from accounts.services.shared import account_management as manage
from accounts.services.shared.sessions import revoke_sessions
from users.services.get_user import get_user


def deactivate_user(*, actor, user_id, reason=None):
    _attempt(actor, user_id, reason)
    return get_user(user_id=user_id)


@transaction.atomic
def _attempt(actor, user_id, reason):
    now = manage.now()
    target = manage.find_user_for_update(user_id)
    manage.ensure_can_remove(actor, target, "deactivate")
    if target.account_status == AccountStatus.SUSPENDED:
        return
    target.account_status = AccountStatus.SUSPENDED
    manage.save_change(actor, target, now)
    revoke_sessions(target, now)
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_DEACTIVATED_ACCOUNT",
        before={"account_status": AccountStatus.ACTIVE},
        after={"account_status": AccountStatus.SUSPENDED},
        reason=reason,
    )
