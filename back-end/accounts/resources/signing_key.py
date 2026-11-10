from rest_framework import serializers


class SigningKeyResource(serializers.Serializer):
    key = serializers.CharField(help_text="A new random value for JWT_SIGNING_KEY.")
    length_bytes = serializers.IntegerField()
    how_to_use = serializers.CharField()
