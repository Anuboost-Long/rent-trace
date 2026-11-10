from rest_framework import serializers

from accounts.models import RoleKind, User


class UserSummaryResource(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    role_names = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "roles",
            "role_names",
            "is_admin",
            "account_status",
            "is_top_level_admin",
            "email_verified_at",
            "last_login_at",
            "created_at",
        ]

    def get_roles(self, user) -> list[str]:
        return [bridge.role.code for bridge in user.active_role_bridges]

    def get_role_names(self, user) -> list[str]:
        return [bridge.role.name for bridge in user.active_role_bridges]

    def get_is_admin(self, user) -> bool:
        return any(bridge.role.kind == RoleKind.ADMIN for bridge in user.active_role_bridges)
