from rest_framework import serializers


class PlaceResource(serializers.Serializer):
    state = serializers.CharField()
    suburb = serializers.CharField()
    listings = serializers.IntegerField()
