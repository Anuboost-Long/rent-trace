from rest_framework import serializers


class ResetLinkQueryDto(serializers.Serializer):
    token = serializers.CharField()
