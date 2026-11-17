from rest_framework import serializers


class MfaCodeDto(serializers.Serializer):
    code = serializers.CharField(
        max_length=32, help_text="A 6-digit authenticator code, or a backup code when verifying."
    )
