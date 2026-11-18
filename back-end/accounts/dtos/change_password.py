from rest_framework import serializers

from accounts.dtos.fields import PasswordField


class ChangePasswordDto(serializers.Serializer):
    current_password = PasswordField()
    new_password = PasswordField()
    sign_out_other_devices = serializers.BooleanField(default=False)
    code = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Authenticator or backup code, needed when the account has two-step verification.",
    )
