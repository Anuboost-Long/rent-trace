from rest_framework import serializers


class MarkedReadResource(serializers.Serializer):
    marked = serializers.IntegerField()
