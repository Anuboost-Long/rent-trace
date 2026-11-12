from django.db import models
from django.db.models import F, Q

from common.models import (
    CatalogueRecord,
    EventRecord,
    MutableRecord,
    enum_check,
    nonblank_check,
)

from .users import User


class RoleKind(models.TextChoices):
    PARTY = "PARTY"
    ADMIN = "ADMIN"


class RoleQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_kind(self, kind):
        return self.filter(kind=kind)

    def with_code(self, code):
        return self.filter(code=code)

    def with_holder_counts(self):
        return self.annotate(
            holder_count=models.Count(
                "user_bridges",
                filter=Q(user_bridges__is_active=True, user_bridges__user__deleted_at__isnull=True),
                distinct=True,
            )
        )

    def with_active_permissions(self):
        return self.prefetch_related(
            models.Prefetch(
                "permission_bridges",
                queryset=RolePermissionBridge.objects.active().select_related("permission"),
                to_attr="active_permission_bridges",
            )
        )


class Role(CatalogueRecord):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    kind = models.TextField(choices=RoleKind, default=RoleKind.ADMIN)
    is_system = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="children"
    )

    objects = RoleQuerySet.as_manager()

    class Meta:
        db_table = "roles"
        constraints = [
            enum_check("roles", "kind", RoleKind),
            models.CheckConstraint(condition=~Q(parent=F("id")), name="ck_roles_parent_not_self"),
        ]


class PermissionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_code(self, code):
        return self.filter(code=code)

    def granted_to_roles(self, role_ids):
        return (
            self.active()
            .filter(role_bridges__is_active=True, role_bridges__role_id__in=role_ids)
            .distinct()
        )

    def granted_to_user(self, user):
        return self.active().filter(user_bridges__user=user, user_bridges__is_active=True)

    def with_active_roles(self):
        return self.prefetch_related(
            models.Prefetch(
                "role_bridges",
                queryset=RolePermissionBridge.objects.active().select_related("role"),
                to_attr="active_role_bridges",
            )
        )


class Permission(CatalogueRecord):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50)
    is_admin_only = models.BooleanField(default=False)

    objects = PermissionQuerySet.as_manager()

    class Meta:
        db_table = "permissions"


class UserRoleBridgeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, role__is_active=True)

    def for_user(self, user):
        return self.filter(user=user)

    def with_kind(self, kind):
        return self.filter(role__kind=kind)

    def with_role(self, role_code):
        return self.filter(role__code=role_code)


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


class RolePermissionBridgeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, permission__is_active=True)


class RolePermissionBridge(MutableRecord):
    role = models.ForeignKey(Role, models.PROTECT, related_name="permission_bridges")
    permission = models.ForeignKey(Permission, models.PROTECT, related_name="role_bridges")
    is_active = models.BooleanField(default=True)

    objects = RolePermissionBridgeQuerySet.as_manager()

    class Meta(MutableRecord.Meta):
        db_table = "role_permission_bridge"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(
                fields=["role", "permission"], name="uq_role_permission_bridge"
            ),
        ]


class UserPermissionBridgeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, permission__is_active=True)

    def for_user(self, user):
        return self.filter(user=user)

    def for_permission(self, permission):
        return self.filter(permission=permission)

    def filter_user_text(self, term):
        return self.filter(
            Q(user__email__icontains=term)
            | Q(user__first_name__icontains=term)
            | Q(user__last_name__icontains=term)
        )

    def newest_first(self):
        return self.order_by("-created_at", "-id")


class UserPermissionBridge(MutableRecord):
    user = models.ForeignKey(User, models.PROTECT, related_name="permission_bridges")
    permission = models.ForeignKey(Permission, models.PROTECT, related_name="user_bridges")
    is_active = models.BooleanField(default=True)
    reason = models.TextField()

    objects = UserPermissionBridgeQuerySet.as_manager()

    class Meta(MutableRecord.Meta):
        db_table = "user_permission_bridge"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(
                fields=["user", "permission"], name="uq_user_permission_bridge"
            ),
            nonblank_check("user_permission_bridge", "reason"),
        ]


class RoleChangeHistory(EventRecord):
    role = models.ForeignKey(Role, models.PROTECT, related_name="change_history")
    action = models.TextField()
    before_values = models.JSONField()
    after_values = models.JSONField()
    reason = models.TextField()

    class Meta:
        db_table = "role_change_history"
        constraints = [
            nonblank_check("role_change_history", "reason"),
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


class AccountAccessHistoryQuerySet(models.QuerySet):
    def with_people(self):
        return self.select_related("user", "created_by")

    def newest_first(self):
        return self.order_by("-created_at", "-id")


class AccountAccessHistory(EventRecord):
    user = models.ForeignKey(User, models.PROTECT, related_name="access_history")
    action = models.TextField()
    before_values = models.JSONField()
    after_values = models.JSONField()
    reason = models.TextField()

    objects = AccountAccessHistoryQuerySet.as_manager()

    class Meta:
        db_table = "account_access_history"
        constraints = [
            nonblank_check("account_access_history", "reason"),
        ]
