from rest_framework.exceptions import ValidationError

from accounts.integrations import emails
from accounts.models import AccountAccessHistory, UserMfa
from accounts.services.shared import account_management as manage
from users.services.get_user import get_user
from users.services.reset_authenticator import RESET_ACTION

NOTHING_TO_RESEND = "This person's authenticator has not been reset."


def resend_authenticator_notice(*, actor, user_id):
    target = get_user(user_id=user_id)
    manage.ensure_can_edit(actor, target)
    if not was_reset(target):
        raise ValidationError(NOTHING_TO_RESEND)
    return emails.send_authenticator_reset(target)


def was_reset(user):
    return (
        not UserMfa.objects.confirmed().filter(user=user).exists()
        and AccountAccessHistory.objects.filter(user=user, action=RESET_ACTION).exists()
    )
