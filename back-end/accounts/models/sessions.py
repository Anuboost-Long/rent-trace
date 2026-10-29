from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower, Trim

from common.models import (
    enum_check,
    nonblank_check,
)

from .users import AuthMethod, User


class AuthTokenPurpose(models.TextChoices):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"


class AuthTokenQuerySet(models.QuerySet):
    def unused(self, now):
        return self.filter(used_at__isnull=True, expires_at__gt=now)

    def matching(self, token_hash, purpose):
        return self.select_related("user").filter(token_hash=token_hash, purpose=purpose)


class AuthToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, models.PROTECT, related_name="auth_tokens")
    purpose = models.TextField(choices=AuthTokenPurpose)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    objects = AuthTokenQuerySet.as_manager()

    class Meta:
        db_table = "auth_tokens"
        constraints = [
            enum_check("auth_tokens", "purpose", AuthTokenPurpose),
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("created_at")),
                name="ck_auth_tokens_expiry",
            ),
            models.CheckConstraint(
                condition=Q(used_at__isnull=True) | Q(used_at__gte=F("created_at")),
                name="ck_auth_tokens_used",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "purpose", "used_at"], name="ix_auth_tokens_user"),
        ]


class AuthSessionQuerySet(models.QuerySet):
    def open(self, now):
        return self.filter(revoked_at__isnull=True, expires_at__gt=now)

    def for_access_token(self, session_id, user_id):
        return self.select_related("user").filter(session_id=session_id, user_id=user_id)


class AuthSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, models.PROTECT, related_name="sessions")
    session_id = models.UUIDField(unique=True)
    verified_method = models.TextField(choices=AuthMethod)
    verified_at = models.DateTimeField()
    mfa_verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField()
    device_name = models.CharField(max_length=150, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    objects = AuthSessionQuerySet.as_manager()

    class Meta:
        db_table = "auth_sessions"
        constraints = [
            enum_check("auth_sessions", "verified_method", AuthMethod),
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("verified_at")),
                name="ck_auth_sessions_expiry",
            ),
            models.CheckConstraint(
                condition=Q(revoked_at__isnull=True)
                | Q(revoked_at__gte=F("verified_at")),
                name="ck_auth_sessions_revoked",
            ),
            models.CheckConstraint(
                condition=Q(mfa_verified_at__isnull=True)
                | Q(mfa_verified_at__gte=F("verified_at")),
                name="ck_auth_sessions_mfa_verified",
            ),
            models.CheckConstraint(
                condition=Q(last_used_at__gte=F("verified_at")),
                name="ck_auth_sessions_last_used",
            ),
        ]


class UserMfa(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, models.PROTECT, related_name="mfa")
    secret_encrypted = models.TextField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    last_used_step = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "user_mfa"
        constraints = [
            nonblank_check("user_mfa", "secret_encrypted"),
        ]


class MfaBackupCode(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, models.PROTECT, related_name="mfa_backup_codes")
    code_hash = models.CharField(max_length=255)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "mfa_backup_codes"
        constraints = [
            nonblank_check("mfa_backup_codes", "code_hash"),
        ]


class RefreshTokenQuerySet(models.QuerySet):
    def matching(self, token_hash):
        return self.select_related("session__user").filter(token_hash=token_hash)


class RefreshToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        AuthSession, models.PROTECT, related_name="refresh_tokens"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    objects = RefreshTokenQuerySet.as_manager()

    class Meta:
        db_table = "refresh_tokens"
        constraints = [
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("created_at")),
                name="ck_refresh_tokens_expiry",
            ),
            models.CheckConstraint(
                condition=Q(used_at__isnull=True) | Q(used_at__gte=F("created_at")),
                name="ck_refresh_tokens_used",
            ),
            models.UniqueConstraint(
                fields=["session"],
                condition=Q(used_at__isnull=True),
                name="uq_refresh_tokens_current",
            ),
        ]


class SignInThrottleQuerySet(models.QuerySet):
    def for_email(self, email_normalized):
        return self.filter(email_normalized=email_normalized)

    def clear(self):
        return self.update(failed_count=0, last_failed_at=None, locked_until=None)


class SignInThrottle(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email_normalized = models.CharField(max_length=255, unique=True)
    failed_count = models.PositiveIntegerField(default=0)
    last_failed_at = models.DateTimeField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)

    objects = SignInThrottleQuerySet.as_manager()

    class Meta:
        db_table = "sign_in_throttles"
        constraints = [
            models.CheckConstraint(
                condition=Q(email_normalized=Lower(Trim("email_normalized"))),
                name="ck_sign_in_throttles_email_normalized",
            ),
            models.CheckConstraint(
                condition=Q(failed_count=0, last_failed_at__isnull=True)
                | Q(failed_count__gt=0, last_failed_at__isnull=False),
                name="ck_sign_in_throttles_last_failed",
            ),
        ]
