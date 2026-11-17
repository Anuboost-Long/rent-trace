from rest_framework import serializers


class PropertyFiguresResource(serializers.Serializer):
    properties = serializers.IntegerField()
    units = serializers.IntegerField()
