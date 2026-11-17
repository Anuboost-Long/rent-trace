from rest_framework import serializers

from accounts.models import Permission


class PermissionResource(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ["code", "name", "module", "is_admin_only", "is_active", "roles"]

    def get_roles(self, permission) -> list[str]:
        return sorted(bridge.role.code for bridge in permission.active_role_bridges)
