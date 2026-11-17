from rest_framework import serializers

TOKEN_STATUSES = ["ACTIVE", "REVOKED", "EXPIRED"]


class TokenListQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Words in the person's name or email or the device.",
    )
    status = serializers.ChoiceField(choices=TOKEN_STATUSES, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
