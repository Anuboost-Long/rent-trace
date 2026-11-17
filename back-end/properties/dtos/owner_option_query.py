from rest_framework import serializers


class OwnerOptionQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False, max_length=100, help_text="Words to find in the email or name."
    )
