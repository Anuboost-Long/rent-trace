import secrets
from enum import StrEnum

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.exceptions import APIException, ValidationError

from accounts.models import MfaBackupCode, UserMfa
from accounts.services.shared.account_rules import is_admin_side

BACKUP_CODE_COUNT = 10
CODE_ACCEPTED_STEPS = (-1, 0, 1)
WRONG_CODE = "That code is incorrect or has already been used."


class MfaStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    ENROL = "ENROL"
    VERIFY = "VERIFY"
    VERIFIED = "VERIFIED"


class MfaUnavailable(APIException):
    status_code = 503
    default_detail = "Two-step verification isn't turned on for this server."
    default_code = "mfa_unavailable"


def mfa_required(user):
    return is_admin_side(user) and not user.is_top_level_admin


def mfa_status(session):
    user = session.user
    enrolled = UserMfa.objects.confirmed().filter(user=user).exists()
    if not enrolled and not mfa_required(user):
        return MfaStatus.NOT_REQUIRED
    if session.mfa_verified_at is not None:
        return MfaStatus.VERIFIED
    return MfaStatus.VERIFY if enrolled else MfaStatus.ENROL


def _fernet():
    try:
        return Fernet(settings.MFA_ENCRYPTION_KEY)
    except (ValueError, TypeError) as error:
        raise MfaUnavailable() from error


def encrypt_secret(secret):
    return _fernet().encrypt(secret.encode()).decode()


def decrypt_secret(secret_encrypted):
    try:
        return _fernet().decrypt(secret_encrypted.encode()).decode()
    except InvalidToken as error:
        raise MfaUnavailable() from error


def new_secret():
    return pyotp.random_base32()


def provisioning_uri(secret, email):
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="RentTrace")


def matching_step(mfa, code, now):
    totp = pyotp.TOTP(decrypt_secret(mfa.secret_encrypted))
    current = totp.timecode(now)
    last_used = mfa.last_used_step or -1
    for offset in CODE_ACCEPTED_STEPS:
        step = current + offset
        if step > last_used and secrets.compare_digest(totp.generate_otp(step), code):
            return step
    return None


def accept_totp_code(mfa, code, now):
    step = matching_step(mfa, code, now)
    if step is None:
        return False
    mfa.last_used_step = step
    mfa.save()
    return True


def new_backup_codes(user):
    raw_codes = [secrets.token_hex(5) for _ in range(BACKUP_CODE_COUNT)]
    MfaBackupCode.objects.bulk_create(
        MfaBackupCode(user=user, code_hash=make_password(code)) for code in raw_codes
    )
    return raw_codes


def accept_backup_code(user, code, now):
    for backup in MfaBackupCode.objects.select_for_update().unused().filter(user=user):
        if check_password(code, backup.code_hash):
            backup.used_at = now
            backup.save()
            return True
    return False


def require_correct(accepted):
    if not accepted:
        raise ValidationError({"code": WRONG_CODE})
