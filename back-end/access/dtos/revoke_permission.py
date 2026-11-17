from rest_framework import serializers


class RevokePermissionDto(serializers.Serializer):
    reason = serializers.CharField(max_length=500, required=False)
