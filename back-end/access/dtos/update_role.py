from rest_framework import serializers


class UpdateRoleDto(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    parent = serializers.CharField(max_length=30, required=False, allow_null=True)
    permissions = serializers.ListField(child=serializers.CharField(max_length=100), required=False)
    is_active = serializers.BooleanField(required=False)
    reason = serializers.CharField(max_length=500, required=False)
