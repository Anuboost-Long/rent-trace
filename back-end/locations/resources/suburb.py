from rest_framework import serializers


class SuburbResource(serializers.Serializer):
    suburb = serializers.CharField()
    postcode = serializers.CharField()
