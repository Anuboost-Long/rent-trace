from rest_framework import serializers

from accounts.models import BanType

BAN_STATUSES = ["ACTIVE", "EXPIRED", "LIFTED"]


class BanListQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False, max_length=100, help_text="Words in the target, reason or person."
    )
    status = serializers.ChoiceField(choices=BAN_STATUSES, required=False)
    type = serializers.ChoiceField(choices=BanType.values, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
