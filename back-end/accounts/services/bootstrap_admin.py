import secrets
import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import connection, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError

from accounts.models import AccountAccessHistory, AuthMethod, User, UserCredential
from accounts.seeds.permissions import ADMIN
from accounts.services.shared.account_rules import EMAIL_IN_USE, assign_role, normalize_email
from accounts.services.shared.passwords import check_password_strength

BOOTSTRAP_LOCK_KEY = 7_204_001
WRONG_SECRET = "The setup secret is incorrect."


class AdminBootstrapUnavailable(APIException):
    status_code = 503
    default_detail = "Admin setup isn't turned on for this server."
    default_code = "admin_bootstrap_unavailable"


class SuperAdminExists(APIException):
    status_code = 409
    default_detail = "A super admin already exists. Sign in with that account to add admins."
    default_code = "super_admin_exists"


def bootstrap_admin(*, secret, email, password, first_name, last_name):
    configured = settings.ADMIN_BOOTSTRAP_SECRET
    if not configured:
        raise AdminBootstrapUnavailable()
    if not secrets.compare_digest(secret.encode(), configured.encode()):
        raise PermissionDenied(WRONG_SECRET)
    _create_super_admin(email, password, first_name, last_name, timezone.now())


@transaction.atomic
def _create_super_admin(email, password, first_name, last_name, now):
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [BOOTSTRAP_LOCK_KEY])
    if User.objects.super_admins().exists():
        raise SuperAdminExists()

    email_normalized = normalize_email(email)
    if User.objects.with_email(email_normalized).exists():
        raise ValidationError({"email": EMAIL_IN_USE})
    check_password_strength(
        password, User(email=email, first_name=first_name, last_name=last_name), "password"
    )

    user = User.objects.create(
        email=email,
        email_normalized=email_normalized,
        email_verified_at=now,
        auth_method=AuthMethod.EMAIL_PASSWORD,
        first_name=first_name,
        last_name=last_name,
        is_top_level_admin=True,
    )
    UserCredential.objects.create(
        user=user, password_hash=make_password(password), password_changed_at=now
    )
    assign_role(user, ADMIN)
    AccountAccessHistory.objects.create(
        user=user,
        action="BOOTSTRAP_SUPER_ADMIN",
        before_values={},
        after_values={"role": ADMIN, "is_top_level_admin": True},
        reason="First super admin created with the server's setup secret",
        correlation_id=uuid.uuid4(),
    )
