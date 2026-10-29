from rest_framework import serializers


class TokenDto(serializers.Serializer):
    token = serializers.CharField()
