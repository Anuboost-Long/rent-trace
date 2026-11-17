from rest_framework import serializers


class EmailDto(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
