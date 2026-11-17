from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.integrations import emails
from accounts.models import AuthTokenPurpose, SignInThrottle, UserMfa
from accounts.services.shared import mfa
from accounts.services.shared.links import use_link
from accounts.services.shared.mail import send_after_commit
from accounts.services.shared.passwords import check_password_strength, replace_password
from accounts.services.shared.sessions import revoke_sessions

LINK_USED_UP = "That code was incorrect, so this link can't be used again. Ask for a new link."


def reset_password(*, raw_token, new_password, sign_out_other_devices, code=None):
    failure = _attempt(raw_token, new_password, sign_out_other_devices, code)
    if failure:
        raise failure


@transaction.atomic
def _attempt(raw_token, new_password, sign_out_other_devices, code):
    """Returns the failure instead of raising it when the link must stay used up."""
    now = timezone.now()
    user = use_link(raw_token, AuthTokenPurpose.PASSWORD_RESET, now)
    enrolment = UserMfa.objects.select_for_update().confirmed().filter(user=user).first()
    if enrolment is not None:
        if not code:
            raise ValidationError({"code": mfa.CODE_NEEDED})
        accepted = mfa.accept_totp_code(enrolment, code, now) or mfa.accept_backup_code(
            user, code, now
        )
        if not accepted:
            return ValidationError({"code": LINK_USED_UP})
    check_password_strength(new_password, user, "new_password")
    replace_password(user, new_password, now)
    if user.email_verified_at is None:
        user.email_verified_at = now
        user.save()
    SignInThrottle.objects.for_email(user.email_normalized).clear()
    if sign_out_other_devices:
        revoke_sessions(user, now)
    send_after_commit(emails.send_password_changed, user)
