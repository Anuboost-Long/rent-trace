from rest_framework import serializers

from accounts.models import Role


class RoleResource(serializers.ModelSerializer):
    parent = serializers.CharField(source="parent.code", default=None, read_only=True)
    holder_count = serializers.IntegerField(read_only=True)
    permissions = serializers.SerializerMethodField()
    inherited_permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "code",
            "name",
            "description",
            "kind",
            "is_system",
            "is_active",
            "parent",
            "holder_count",
            "permissions",
            "inherited_permissions",
        ]

    def get_permissions(self, role) -> list[str]:
        return sorted(bridge.permission.code for bridge in role.active_permission_bridges)

    def get_inherited_permissions(self, role) -> list[str]:
        return sorted(role.inherited_codes)
