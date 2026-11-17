from rest_framework import serializers

from access.resources.permission import PermissionResource
from accounts.models import UserPermissionBridge
from accounts.resources.user_brief import UserBriefResource


class HolderRoleResource(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    inherited = serializers.BooleanField(help_text="True when it comes from a parent role.")


class HolderGrantResource(serializers.ModelSerializer):
    user = UserBriefResource()
    granted_by = serializers.SerializerMethodField()

    class Meta:
        model = UserPermissionBridge
        fields = ["user", "reason", "created_at", "granted_by"]

    def get_granted_by(self, grant) -> dict | None:
        actor = grant.updated_by or grant.created_by
        return UserBriefResource(actor).data if actor else None


class PermissionHoldersResource(serializers.Serializer):
    permission = PermissionResource()
    roles = HolderRoleResource(many=True)
    people_through_roles = serializers.IntegerField()
    grants = HolderGrantResource(many=True)
