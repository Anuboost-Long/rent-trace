from django.db import models
from django.db.models import F, Prefetch, Q
from django.db.models.functions import Lower, Trim
from django.db.models.lookups import Exact

from common.models import (
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


class UserQuerySet(models.QuerySet):
    def with_email(self, email_normalized):
        return self.filter(email_normalized=email_normalized)

    def with_subject(self, auth_subject):
        return self.filter(auth_subject=auth_subject)

    def password_accounts(self):
        return self.filter(auth_method=AuthMethod.EMAIL_PASSWORD)

    def google_accounts(self):
        return self.filter(auth_method=AuthMethod.GOOGLE)

    def not_deleted(self):
        return self.filter(deleted_at__isnull=True)

    def search(self, text):
        matches = self
        for term in text.split():
            matches = matches.filter(
                Q(email__icontains=term)
                | Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
            )
        return matches

    def with_role(self, role_code):
        return self.filter(
            role_bridges__is_active=True,
            role_bridges__role__is_active=True,
            role_bridges__role__code=role_code,
        )

    def with_any_role(self, role_ids):
        return self.filter(
            role_bridges__is_active=True, role_bridges__role_id__in=role_ids
        ).distinct()

    def with_status(self, account_status):
        return self.filter(account_status=account_status)

    def with_active_roles(self):
        from accounts.models.access import UserRoleBridge

        active_bridges = UserRoleBridge.objects.active().select_related("role")
        return self.prefetch_related(
            Prefetch("role_bridges", queryset=active_bridges, to_attr="active_role_bridges")
        )

    def newest_first(self):
        return self.order_by("-created_at", "-id")

    def super_admins(self):
        return self.filter(is_top_level_admin=True)

    def unverified(self):
        return self.filter(email_verified_at__isnull=True)


class User(MutableRecord):
    auth_subject = models.UUIDField(unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255)
    email_normalized = models.CharField(max_length=255, unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    auth_method = models.TextField(choices=AuthMethod)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    account_status = models.TextField(choices=AccountStatus, default=AccountStatus.ACTIVE)
    is_top_level_admin = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True)

    objects = UserQuerySet.as_manager()

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
                condition=~Q(auth_method=AuthMethod.GOOGLE) | Q(email_verified_at__isnull=False),
                name="ck_users_google_verified",
            ),
        ]

    @property
    def is_authenticated(self):
        return True


class UserCredentialQuerySet(models.QuerySet):
    def for_email(self, email_normalized):
        return self.select_related("user").filter(user__email_normalized=email_normalized)


class UserCredential(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, models.PROTECT, related_name="credential")
    password_hash = models.CharField(max_length=255)
    password_changed_at = models.DateTimeField()

    objects = UserCredentialQuerySet.as_manager()

    class Meta:
        db_table = "user_credentials"
        constraints = [
            nonblank_check("user_credentials", "password_hash"),
        ]


class BanType(models.TextChoices):
    EMAIL = "EMAIL"
    EMAIL_DOMAIN = "EMAIL_DOMAIN"
    PHONE = "PHONE"
    ACCOUNT = "ACCOUNT"


class BanQuerySet(models.QuerySet):
    def active(self, now):
        return self.filter(lifted_at__isnull=True, deleted_at__isnull=True).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        )

    def for_identity(self, email_normalized):
        domain = email_normalized.rsplit("@", 1)[-1]
        return self.filter(
            Q(ban_type=BanType.EMAIL, value=email_normalized)
            | Q(ban_type=BanType.EMAIL_DOMAIN, value=domain)
        )

    def for_account(self, user):
        return self.filter(ban_type=BanType.ACCOUNT, user=user)

    def with_people(self):
        return self.select_related("user", "created_by", "lifted_by")

    def with_type(self, ban_type):
        return self.filter(ban_type=ban_type)

    def with_status(self, status, now):
        if status == "ACTIVE":
            return self.active(now)
        if status == "LIFTED":
            return self.filter(lifted_at__isnull=False)
        return self.filter(lifted_at__isnull=True, expires_at__lte=now)

    def search(self, text):
        matches = self
        for term in text.split():
            matches = matches.filter(
                Q(value__icontains=term)
                | Q(reason__icontains=term)
                | Q(user__email__icontains=term)
                | Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
            )
        return matches

    def newest_first(self):
        return self.order_by("-created_at", "-id")


class Ban(MutableRecord):
    ban_type = models.TextField(choices=BanType)
    value = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, models.PROTECT, null=True, blank=True, related_name="bans")
    reason = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    lifted_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.ForeignKey(User, models.PROTECT, null=True, blank=True, related_name="+")
    lift_reason = models.TextField(null=True, blank=True)

    objects = BanQuerySet.as_manager()

    class Meta(MutableRecord.Meta):
        db_table = "ban_list"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("ban_list", "ban_type", BanType),
            nonblank_check("ban_list", "reason"),
            models.CheckConstraint(
                condition=Q(ban_type=BanType.ACCOUNT, user__isnull=False, value__isnull=True)
                | Q(user__isnull=True, value=Lower(Trim("value"))) & ~Q(ban_type=BanType.ACCOUNT),
                name="ck_ban_list_target",
            ),
            models.CheckConstraint(
                condition=Q(
                    lifted_at__isnull=True, lifted_by__isnull=True, lift_reason__isnull=True
                )
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
                condition=Q(lifted_at__isnull=True, deleted_at__isnull=True, user__isnull=True),
                name="uq_ban_list_current_identity",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(lifted_at__isnull=True, deleted_at__isnull=True, user__isnull=False),
                name="uq_ban_list_current_account",
            ),
        ]
