from rest_framework import serializers


class ResetPreviewResource(serializers.Serializer):
    requires_code = serializers.BooleanField(
        help_text="True when the reset also needs an authenticator or backup code."
    )
