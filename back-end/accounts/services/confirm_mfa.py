from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import UserMfa
from accounts.services.shared import mfa


@transaction.atomic
def confirm_mfa(*, user, session, code):
    now = timezone.now()
    enrolment = UserMfa.objects.select_for_update().filter(user=user).first()
    if enrolment is None or enrolment.confirmed_at is not None:
        raise ValidationError("Start two-step verification setup first.")
    mfa.require_correct(mfa.accept_totp_code(enrolment, code, now))

    enrolment.confirmed_at = now
    enrolment.save()
    session.mfa_verified_at = now
    session.save()
    return mfa.new_backup_codes(user)
