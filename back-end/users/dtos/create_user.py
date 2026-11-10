from rest_framework import serializers

from accounts.dtos.fields import PasswordField


class CreateUserDto(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = PasswordField(help_text="The starting password. Share it with the person securely.")
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    roles = serializers.ListField(
        child=serializers.CharField(max_length=30),
        min_length=1,
        help_text="Role codes: one of TENANT or LANDLORD, or one or more admin roles.",
    )
