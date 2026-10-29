from rest_framework import serializers


class MessageResource(serializers.Serializer):
    detail = serializers.CharField()
