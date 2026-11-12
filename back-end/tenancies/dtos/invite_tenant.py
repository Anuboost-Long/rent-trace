from rest_framework import serializers


class InviteTenantDto(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    is_primary = serializers.BooleanField(required=False, default=False)
