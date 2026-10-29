from rest_framework import serializers

from accounts.resources.user import UserResource


class SignedInResource(serializers.Serializer):
    token_type = serializers.CharField(default="Bearer")
    access_token = serializers.CharField()
    expires_in = serializers.IntegerField(help_text="Seconds until the access token expires.")
    refresh_token = serializers.CharField()
    needs_onboarding = serializers.BooleanField()
    user = UserResource()
