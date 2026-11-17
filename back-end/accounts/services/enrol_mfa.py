from django.db import transaction
from rest_framework.exceptions import APIException, PermissionDenied

from accounts.models import UserMfa
from accounts.services.shared import mfa
from accounts.services.shared.account_rules import is_admin_side


class MfaAlreadyEnrolled(APIException):
    status_code = 409
    default_detail = "Two-step verification is already set up for this account."
    default_code = "mfa_already_enrolled"


@transaction.atomic
def enrol_mfa(*, user):
    if not is_admin_side(user):
        raise PermissionDenied("Two-step verification is only for admin accounts.")
    existing = UserMfa.objects.select_for_update().filter(user=user).first()
    if existing is not None and existing.confirmed_at is not None:
        raise MfaAlreadyEnrolled()
    if existing is None:
        secret = mfa.new_secret()
        UserMfa.objects.create(user=user, secret_encrypted=mfa.encrypt_secret(secret))
    else:
        secret = mfa.decrypt_secret(existing.secret_encrypted)
    return secret, mfa.provisioning_uri(secret, user.email)
