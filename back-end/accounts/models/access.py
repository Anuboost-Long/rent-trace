from django.db import models
from django.db.models import Q

from common.models import (
    CatalogueRecord,
    EventRecord,
    MutableRecord,
    enum_check,
    nonblank_check,
)

from .users import User


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


class UserRoleBridgeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, role__is_active=True)


class UserRoleBridge(MutableRecord):
    user = models.ForeignKey(User, models.PROTECT, related_name="role_bridges")
    role = models.ForeignKey(Role, models.PROTECT, related_name="user_bridges")
    is_active = models.BooleanField(default=True)

    objects = UserRoleBridgeQuerySet.as_manager()

    class Meta(MutableRecord.Meta):
        db_table = "user_role_bridge"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(fields=["user", "role"], name="uq_user_role_bridge"),
        ]


class RolePermissionBridge(MutableRecord):
    role = models.ForeignKey(Role, models.PROTECT, related_name="permission_bridges")
    permission = models.ForeignKey(Permission, models.PROTECT, related_name="role_bridges")
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
    user = models.ForeignKey(User, models.PROTECT, related_name="permission_bridges")
    permission = models.ForeignKey(Permission, models.PROTECT, related_name="user_bridges")
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
