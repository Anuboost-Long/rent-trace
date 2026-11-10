from rest_framework import serializers

from accounts.dtos.fields import PasswordField


class BootstrapAdminDto(serializers.Serializer):
    secret = serializers.CharField(
        help_text="The value of ADMIN_BOOTSTRAP_SECRET in the server's config/.env."
    )
    email = serializers.EmailField(max_length=255)
    password = PasswordField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
