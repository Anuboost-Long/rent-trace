import uuid
from dataclasses import dataclass

from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import AccountAccessHistory, AuthMethod, User, UserCredential
from accounts.services.shared import role_assignment
from accounts.services.shared.account_rules import (
    EMAIL_IN_USE,
    is_identity_banned,
    normalize_email,
)
from accounts.services.shared.passwords import check_password_strength
from users.services.get_user import get_user

EMAIL_BANNED = "This email can't be used."


@dataclass(frozen=True)
class NewUser:
    email: str
    password: str
    first_name: str
    last_name: str
    role_codes: list[str]


def create_user(*, actor, new_user):
    now = timezone.now()
    email_normalized = normalize_email(new_user.email)
    roles = role_assignment.resolve_roles(new_user.role_codes)
    check_password_strength(
        new_user.password,
        User(email=new_user.email, first_name=new_user.first_name, last_name=new_user.last_name),
        "password",
    )
    if is_identity_banned(email_normalized, now):
        raise ValidationError({"email": EMAIL_BANNED})
    try:
        user_id = _register(actor, new_user, roles, email_normalized, now)
    except IntegrityError as error:
        raise ValidationError({"email": EMAIL_IN_USE}) from error
    return get_user(user_id=user_id)


@transaction.atomic
def _register(actor, new_user, roles, email_normalized, now):
    if User.objects.with_email(email_normalized).exists():
        raise ValidationError({"email": EMAIL_IN_USE})
    user = User.objects.create(
        email=new_user.email,
        email_normalized=email_normalized,
        email_verified_at=now,
        auth_method=AuthMethod.EMAIL_PASSWORD,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        created_by=actor,
    )
    UserCredential.objects.create(
        user=user, password_hash=make_password(new_user.password), password_changed_at=now
    )
    role_assignment.change_roles(actor, user, roles)
    AccountAccessHistory.objects.create(
        user=user,
        action="ADMIN_CREATED_ACCOUNT",
        before_values={},
        after_values={"roles": sorted(role.code for role in roles), "email_verified": True},
        reason=f"Account created by admin {actor.pk}",
        correlation_id=uuid.uuid4(),
        created_by=actor,
    )
    return user.pk
