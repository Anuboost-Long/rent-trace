from django.core.validators import RegexValidator
from rest_framework import serializers

PHONE_NUMBER = RegexValidator(
    r"^\+?[0-9 ()\-]{6,30}$",
    "Use digits, spaces, dashes and brackets, with an optional leading +.",
)


class UpdateProfileDto(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone_number = serializers.CharField(
        max_length=30,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[PHONE_NUMBER],
    )
