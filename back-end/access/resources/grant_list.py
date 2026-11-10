from rest_framework import serializers

from access.resources.permission_holders import HolderGrantResource
from accounts.models import UserPermissionBridge
from accounts.resources.user_brief import UserBriefResource


class GrantListItemResource(HolderGrantResource):
    permission_code = serializers.CharField(source="permission.code")
    permission_name = serializers.CharField(source="permission.name")

    class Meta:
        model = UserPermissionBridge
        fields = [*HolderGrantResource.Meta.fields, "permission_code", "permission_name"]


class GrantPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = GrantListItemResource(many=True)


__all__ = ["GrantListItemResource", "GrantPageResource", "UserBriefResource"]
