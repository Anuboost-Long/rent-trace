from rest_framework import serializers


class RefreshDto(serializers.Serializer):
    refresh_token = serializers.CharField()
