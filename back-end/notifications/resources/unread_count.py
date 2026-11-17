from rest_framework import serializers


class UnreadCountResource(serializers.Serializer):
    unread = serializers.IntegerField()
