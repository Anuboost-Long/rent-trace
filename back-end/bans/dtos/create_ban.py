from django.utils import timezone
from rest_framework import serializers

from accounts.models import BanType

CREATABLE_TYPES = [BanType.EMAIL, BanType.EMAIL_DOMAIN, BanType.ACCOUNT]


def _account_target(attrs):
    if "user_id" not in attrs:
        raise serializers.ValidationError({"user_id": "Choose the person to ban."})
    attrs.pop("value", None)


def _email_target(value):
    if "@" not in value:
        raise serializers.ValidationError({"value": "Enter a full email address."})
    return value


def _domain_target(value):
    domain = value.removeprefix("@")
    if "@" in domain or "." not in domain:
        raise serializers.ValidationError({"value": "Enter a domain like example.com."})
    return domain


class CreateBanDto(serializers.Serializer):
    ban_type = serializers.ChoiceField(choices=CREATABLE_TYPES)
    value = serializers.CharField(
        required=False, max_length=255, help_text="The email or domain. Not used for accounts."
    )
    user_id = serializers.IntegerField(
        required=False, help_text="The person to ban. Only used for accounts."
    )
    reason = serializers.CharField(max_length=500)
    expires_at = serializers.DateTimeField(
        required=False, allow_null=True, help_text="Leave empty for a ban that never ends."
    )

    def validate_expires_at(self, expires_at):
        if expires_at is not None and expires_at <= timezone.now():
            raise serializers.ValidationError("Choose a time in the future.")
        return expires_at

    def validate(self, attrs):
        if attrs["ban_type"] == BanType.ACCOUNT:
            _account_target(attrs)
            return attrs
        value = attrs.get("value", "").strip().lower()
        if not value:
            raise serializers.ValidationError({"value": "Enter the email or domain to ban."})
        check = _email_target if attrs["ban_type"] == BanType.EMAIL else _domain_target
        attrs["value"] = check(value)
        attrs.pop("user_id", None)
        return attrs
