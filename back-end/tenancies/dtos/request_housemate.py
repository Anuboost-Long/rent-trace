from rest_framework import serializers


class RequestHousemateDto(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
