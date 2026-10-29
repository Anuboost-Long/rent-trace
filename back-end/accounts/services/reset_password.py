from django.db import transaction
from django.utils import timezone

from accounts.models import AuthTokenPurpose, SignInThrottle
from accounts.services.shared.links import use_link
from accounts.services.shared.passwords import check_password_strength, replace_password
from accounts.services.shared.sessions import revoke_sessions


@transaction.atomic
def reset_password(*, raw_token, new_password, sign_out_other_devices):
    now = timezone.now()
    user = use_link(raw_token, AuthTokenPurpose.PASSWORD_RESET, now)
    check_password_strength(new_password, user, "new_password")
    replace_password(user, new_password, now)
    if user.email_verified_at is None:
        user.email_verified_at = now
        user.save()
    SignInThrottle.objects.for_email(user.email_normalized).clear()
    if sign_out_other_devices:
        revoke_sessions(user, now)
