import uuid
from dataclasses import dataclass
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.integrations import emails
from accounts.models import AccountAccessHistory, AuthMethod, AuthTokenPurpose, User, UserCredential
from accounts.services.shared.account_rules import assign_role, is_identity_banned, normalize_email
from accounts.services.shared.links import VERIFICATION_LINK_LIFETIME, issue_link
from accounts.services.shared.mail import send_after_commit
from accounts.services.shared.passwords import check_password_strength


UNVERIFIED_RECLAIM_AFTER = timedelta(days=7)


@dataclass(frozen=True)
class Applicant:
    email: str
    email_normalized: str
    password: str
    first_name: str
    last_name: str
    role_code: str


def sign_up(*, email, password, first_name, last_name, role_code):
    now = timezone.now()
    applicant = Applicant(email, normalize_email(email), password, first_name, last_name, role_code)
    check_password_strength(
        password, User(email=email, first_name=first_name, last_name=last_name), "password"
    )
    if is_identity_banned(applicant.email_normalized, now):
        return
    try:
        _register(applicant, now)
    except IntegrityError:
        return


@transaction.atomic
def _register(applicant, now):
    user = User.objects.select_for_update().with_email(applicant.email_normalized).first()
    if user is not None and _is_taken(user):
        send_after_commit(emails.send_already_registered, user)
        return

    if user is None:
        user = _create_account(applicant, now)
    if now - user.created_at >= UNVERIFIED_RECLAIM_AFTER:
        _reclaim(user, applicant, now)

    raw = issue_link(user, AuthTokenPurpose.EMAIL_VERIFICATION, VERIFICATION_LINK_LIFETIME, now)
    send_after_commit(emails.send_verification, user, raw)


def _is_taken(user):
    return user.email_verified_at is not None or user.auth_method != AuthMethod.EMAIL_PASSWORD


def _create_account(applicant, now):
    user = User.objects.create(
        email=applicant.email,
        email_normalized=applicant.email_normalized,
        auth_method=AuthMethod.EMAIL_PASSWORD,
        first_name=applicant.first_name,
        last_name=applicant.last_name,
    )
    UserCredential.objects.create(
        user=user, password_hash=make_password(applicant.password), password_changed_at=now
    )
    assign_role(user, applicant.role_code)
    return user


def _reclaim(user, applicant, now):
    before = {"first_name": user.first_name, "last_name": user.last_name}
    user.first_name, user.last_name = applicant.first_name, applicant.last_name
    user.save()
    user.credential.password_hash = make_password(applicant.password)
    user.credential.password_changed_at = now
    user.credential.save()
    assign_role(user, applicant.role_code)
    AccountAccessHistory.objects.create(
        user=user,
        action="RECLAIM_UNVERIFIED",
        before_values=before,
        after_values={
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "role": applicant.role_code,
        },
        reason=f"Signed up again after the account stayed unverified for {UNVERIFIED_RECLAIM_AFTER.days} days",
        correlation_id=uuid.uuid4(),
    )
