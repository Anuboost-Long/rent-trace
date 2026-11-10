from rest_framework import serializers


class UpdateUserDto(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone_number = serializers.CharField(
        max_length=30, required=False, allow_null=True, allow_blank=True
    )
    roles = serializers.ListField(
        child=serializers.CharField(max_length=30), min_length=1, required=False
    )
