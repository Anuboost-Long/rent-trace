from rest_framework import serializers


class UpdatePermissionDto(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=False)
    is_admin_only = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
