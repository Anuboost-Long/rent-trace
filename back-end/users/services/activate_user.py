from django.db import transaction

from accounts.models import AccountStatus
from accounts.services.shared import account_management as manage
from users.services.get_user import get_user


def activate_user(*, actor, user_id, reason=None):
    _attempt(actor, user_id, reason)
    return get_user(user_id=user_id)


@transaction.atomic
def _attempt(actor, user_id, reason):
    now = manage.now()
    target = manage.find_user_for_update(user_id)
    manage.ensure_can_edit(actor, target)
    if target.account_status == AccountStatus.ACTIVE:
        return
    target.account_status = AccountStatus.ACTIVE
    manage.save_change(actor, target, now)
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_ACTIVATED_ACCOUNT",
        before={"account_status": AccountStatus.SUSPENDED},
        after={"account_status": AccountStatus.ACTIVE},
        reason=reason,
    )
