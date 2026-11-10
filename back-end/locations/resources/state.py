from rest_framework import serializers


class StateResource(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
