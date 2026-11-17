from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.integrations import emails
from accounts.models import UserCredential
from accounts.services.shared import mfa
from accounts.services.shared.mail import send_after_commit
from accounts.services.shared.passwords import check_password_strength, replace_password
from accounts.services.shared.sessions import revoke_sessions


@transaction.atomic
def change_password(
    *, user, session, current_password, new_password, sign_out_other_devices, code=None
):
    now = timezone.now()
    credential = UserCredential.objects.select_for_update().filter(user=user).first()
    if credential is None:
        raise ValidationError(
            {"current_password": "This account signs in with Google, so it has no password."}
        )
    if not check_password(current_password, credential.password_hash):
        raise ValidationError({"current_password": "Current password is incorrect."})
    mfa.require_code_if_enrolled(user, code, now)
    check_password_strength(new_password, user, "new_password")
    replace_password(user, new_password, now)
    if sign_out_other_devices:
        revoke_sessions(user, now, keep=session)
    send_after_commit(emails.send_password_changed, user)
