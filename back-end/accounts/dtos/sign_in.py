from rest_framework import serializers

from accounts.dtos.fields import PasswordField


class SignInDto(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = PasswordField()
    device_name = serializers.CharField(max_length=150, required=False)
