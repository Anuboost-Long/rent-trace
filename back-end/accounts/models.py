from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower, Trim
from django.db.models.lookups import Exact

from common.models import (
    CatalogueRecord,
    EventRecord,
    MutableRecord,
    enum_check,
    nonblank_check,
)


class AuthMethod(models.TextChoices):
    GOOGLE = "GOOGLE"
    EMAIL_PASSWORD = "EMAIL_PASSWORD"


class AccountStatus(models.TextChoices):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class User(MutableRecord):
    auth_subject = models.UUIDField(unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255)
    email_normalized = models.CharField(max_length=255, unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    auth_method = models.TextField(choices=AuthMethod)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    account_status = models.TextField(
        choices=AccountStatus, default=AccountStatus.ACTIVE
    )
    is_top_level_admin = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "users"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("users", "auth_method", AuthMethod),
            enum_check("users", "account_status", AccountStatus),
            models.CheckConstraint(
                condition=Q(email_normalized=Lower(Trim("email"))),
                name="ck_users_email_normalized",
            ),
            nonblank_check("users", "first_name"),
            nonblank_check("users", "last_name"),
            models.CheckConstraint(
                condition=Q(auth_method=AuthMethod.GOOGLE, auth_subject__isnull=False)
                | Q(auth_method=AuthMethod.EMAIL_PASSWORD, auth_subject__isnull=True),
                name="ck_users_auth_subject",
            ),
            models.CheckConstraint(
                condition=~Q(auth_method=AuthMethod.GOOGLE)
                | Q(email_verified_at__isnull=False),
                name="ck_users_google_verified",
            ),
        ]


class UserCredential(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, models.PROTECT, related_name="credential")
    password_hash = models.CharField(max_length=255)
    password_changed_at = models.DateTimeField()

    class Meta:
        db_table = "user_credentials"
        constraints = [
            nonblank_check("user_credentials", "password_hash"),
        ]


class AuthTokenPurpose(models.TextChoices):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"


class AuthToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, models.PROTECT, related_name="auth_tokens")
    purpose = models.TextField(choices=AuthTokenPurpose)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

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


class RefreshToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        AuthSession, models.PROTECT, related_name="refresh_tokens"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

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


class SignInThrottle(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email_normalized = models.CharField(max_length=255, unique=True)
    failed_count = models.PositiveIntegerField(default=0)
    last_failed_at = models.DateTimeField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)

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


class Role(CatalogueRecord):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "roles"


class Permission(CatalogueRecord):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50)

    class Meta:
        db_table = "permissions"


class UserRoleBridge(MutableRecord):
    user = models.ForeignKey(User, models.PROTECT, related_name="role_bridges")
    role = models.ForeignKey(Role, models.PROTECT, related_name="user_bridges")
    is_active = models.BooleanField(default=True)

    class Meta(MutableRecord.Meta):
        db_table = "user_role_bridge"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(fields=["user", "role"], name="uq_user_role_bridge"),
        ]


class RolePermissionBridge(MutableRecord):
    role = models.ForeignKey(Role, models.PROTECT, related_name="permission_bridges")
    permission = models.ForeignKey(
        Permission, models.PROTECT, related_name="role_bridges"
    )
    is_active = models.BooleanField(default=True)

    class Meta(MutableRecord.Meta):
        db_table = "role_permission_bridge"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(
                fields=["role", "permission"], name="uq_role_permission_bridge"
            ),
        ]


class UserPermissionBridge(MutableRecord):
    user = models.ForeignKey(
        User, models.PROTECT, related_name="permission_bridges"
    )
    permission = models.ForeignKey(
        Permission, models.PROTECT, related_name="user_bridges"
    )
    is_active = models.BooleanField(default=True)
    reason = models.TextField()

    class Meta(MutableRecord.Meta):
        db_table = "user_permission_bridge"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(
                fields=["user", "permission"], name="uq_user_permission_bridge"
            ),
            nonblank_check("user_permission_bridge", "reason"),
        ]


class HiddenRecordsMode(models.TextChoices):
    DENY_ALL = "DENY_ALL"
    EXPLICIT_TOP_LEVEL = "EXPLICIT_TOP_LEVEL"


class AccessPolicy(MutableRecord):
    hidden_records_mode = models.TextField(
        choices=HiddenRecordsMode, default=HiddenRecordsMode.DENY_ALL
    )

    class Meta(MutableRecord.Meta):
        db_table = "access_policy"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.CheckConstraint(condition=Q(id=1), name="ck_access_policy_singleton"),
            enum_check("access_policy", "hidden_records_mode", HiddenRecordsMode),
        ]


class AccountAccessHistory(EventRecord):
    user = models.ForeignKey(User, models.PROTECT, related_name="access_history")
    action = models.TextField()
    before_values = models.JSONField()
    after_values = models.JSONField()
    reason = models.TextField()

    class Meta:
        db_table = "account_access_history"
        constraints = [
            nonblank_check("account_access_history", "reason"),
        ]


class BanType(models.TextChoices):
    EMAIL = "EMAIL"
    EMAIL_DOMAIN = "EMAIL_DOMAIN"
    PHONE = "PHONE"
    ACCOUNT = "ACCOUNT"


class Ban(MutableRecord):
    ban_type = models.TextField(choices=BanType)
    value = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, models.PROTECT, null=True, blank=True, related_name="bans")
    reason = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    lifted_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.ForeignKey(User, models.PROTECT, null=True, blank=True, related_name="+")
    lift_reason = models.TextField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "ban_list"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("ban_list", "ban_type", BanType),
            nonblank_check("ban_list", "reason"),
            models.CheckConstraint(
                condition=Q(ban_type=BanType.ACCOUNT, user__isnull=False, value__isnull=True)
                | Q(user__isnull=True, value=Lower(Trim("value")))
                & ~Q(ban_type=BanType.ACCOUNT),
                name="ck_ban_list_target",
            ),
            models.CheckConstraint(
                condition=Q(lifted_at__isnull=True, lifted_by__isnull=True, lift_reason__isnull=True)
                | Q(lifted_at__isnull=False, lifted_by__isnull=False, lift_reason__isnull=False)
                & ~Q(Exact(Trim("lift_reason"), "")),
                name="ck_ban_list_lift",
            ),
            models.CheckConstraint(
                condition=Q(expires_at__isnull=True) | Q(expires_at__gt=F("created_at")),
                name="ck_ban_list_expiry",
            ),
            models.UniqueConstraint(
                fields=["ban_type", "value"],
                condition=Q(lifted_at__isnull=True, is_deleted=False, user__isnull=True),
                name="uq_ban_list_current_identity",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(lifted_at__isnull=True, is_deleted=False, user__isnull=False),
                name="uq_ban_list_current_account",
            ),
        ]
