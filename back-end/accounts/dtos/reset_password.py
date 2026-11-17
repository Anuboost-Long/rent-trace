from rest_framework import serializers

from accounts.dtos.fields import PasswordField


class ResetPasswordDto(serializers.Serializer):
    token = serializers.CharField()
    new_password = PasswordField()
    sign_out_other_devices = serializers.BooleanField(default=True)
