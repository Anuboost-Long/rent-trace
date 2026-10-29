from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import UserCredential
from accounts.services.shared.passwords import check_password_strength, replace_password
from accounts.services.shared.sessions import revoke_sessions


@transaction.atomic
def change_password(*, user, session, current_password, new_password, sign_out_other_devices):
    now = timezone.now()
    credential = UserCredential.objects.select_for_update().filter(user=user).first()
    if credential is None:
        raise ValidationError({"current_password": "This account signs in with Google, so it has no password."})
    if not check_password(current_password, credential.password_hash):
        raise ValidationError({"current_password": "Current password is incorrect."})
    check_password_strength(new_password, user, "new_password")
    replace_password(user, new_password, now)
    if sign_out_other_devices:
        revoke_sessions(user, now, keep=session)
