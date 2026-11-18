from rest_framework import serializers


class ResetAuthenticatorDto(serializers.Serializer):
    reason = serializers.CharField(
        max_length=500, help_text="Saved in the account's history. Say how you confirmed who asked."
    )
