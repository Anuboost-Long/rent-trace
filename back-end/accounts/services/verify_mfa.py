from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import UserMfa
from accounts.services.shared import mfa


@transaction.atomic
def verify_mfa(*, user, session, code):
    now = timezone.now()
    enrolment = UserMfa.objects.select_for_update().confirmed().filter(user=user).first()
    if enrolment is None:
        raise ValidationError("Set up two-step verification first.")
    accepted = mfa.accept_totp_code(enrolment, code, now) or mfa.accept_backup_code(user, code, now)
    mfa.require_correct(accepted)

    session.mfa_verified_at = now
    session.save()
