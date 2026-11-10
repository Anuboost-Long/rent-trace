from rest_framework import serializers

from accounts.models import UserPermissionBridge


class PermissionSummaryResource(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    module = serializers.CharField()


class GrantResource(serializers.ModelSerializer):
    code = serializers.CharField(source="permission.code")
    name = serializers.CharField(source="permission.name")
    module = serializers.CharField(source="permission.module")

    class Meta:
        model = UserPermissionBridge
        fields = ["code", "name", "module", "reason", "is_active", "created_at"]


class UserPermissionsResource(serializers.Serializer):
    roles = serializers.ListField(child=serializers.CharField())
    through_roles = PermissionSummaryResource(many=True)
    grants = GrantResource(many=True)
    effective = serializers.ListField(child=serializers.CharField())
