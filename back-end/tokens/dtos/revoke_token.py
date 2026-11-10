from rest_framework import serializers


class RevokeTokenDto(serializers.Serializer):
    reason = serializers.CharField(max_length=500, required=False)
