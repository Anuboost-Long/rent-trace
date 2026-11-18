from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.integrations import emails
from accounts.models import MfaBackupCode, UserMfa
from accounts.services.shared import account_management as manage
from accounts.services.shared.mail import send_after_commit
from accounts.services.shared.sessions import revoke_sessions
from users.services.get_user import get_user

NOT_SET_UP = "This person has not set up an authenticator."


def reset_authenticator(*, actor, user_id, reason):
    _attempt(actor, user_id, reason)
    return get_user(user_id=user_id)


@transaction.atomic
def _attempt(actor, user_id, reason):
    now = manage.now()
    target = manage.find_user_for_update(user_id)
    manage.ensure_can_edit(actor, target)
    if target.pk == actor.pk:
        raise ValidationError("You can't reset your own authenticator.")
    if not UserMfa.objects.filter(user=target).exists():
        raise ValidationError(NOT_SET_UP)
    unused_backup_codes = MfaBackupCode.objects.unused().filter(user=target).count()
    MfaBackupCode.objects.filter(user=target).delete()
    UserMfa.objects.filter(user=target).delete()
    revoke_sessions(target, now)
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_RESET_AUTHENTICATOR",
        before={"authenticator": "SET_UP", "unused_backup_codes": unused_backup_codes},
        after={"authenticator": "NOT_SET_UP", "unused_backup_codes": 0},
        reason=reason,
    )
    send_after_commit(emails.send_authenticator_reset, target)
