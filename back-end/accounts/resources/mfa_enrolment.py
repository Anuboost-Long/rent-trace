from rest_framework import serializers


class MfaEnrolmentResource(serializers.Serializer):
    secret = serializers.CharField(help_text="For typing into an authenticator app by hand.")
    provisioning_uri = serializers.CharField(help_text="An otpauth:// link to show as a QR code.")
