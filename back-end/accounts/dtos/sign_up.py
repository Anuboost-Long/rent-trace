from rest_framework import serializers

from accounts.dtos.fields import SELF_SERVICE_ROLES, PasswordField


class SignUpDto(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = PasswordField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(choices=SELF_SERVICE_ROLES)
