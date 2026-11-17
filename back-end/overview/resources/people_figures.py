from rest_framework import serializers


class PeopleFiguresResource(serializers.Serializer):
    users = serializers.IntegerField()
    suspended = serializers.IntegerField()
