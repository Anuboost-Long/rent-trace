from rest_framework import serializers

from accounts.resources.user import UserResource
from accounts.services.shared.mfa import MfaStatus


class SignedInResource(serializers.Serializer):
    token_type = serializers.CharField(default="Bearer")
    access_token = serializers.CharField()
    expires_in = serializers.IntegerField(help_text="Seconds until the access token expires.")
    refresh_token = serializers.CharField()
    needs_onboarding = serializers.BooleanField()
    mfa_status = serializers.ChoiceField(choices=[status.value for status in MfaStatus])
    user = UserResource()
