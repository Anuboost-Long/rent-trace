from rest_framework import serializers


class GoogleSignInDto(serializers.Serializer):
    access_token = serializers.CharField(help_text="Supabase access token from the Google sign-in.")
    device_name = serializers.CharField(max_length=150, required=False)
