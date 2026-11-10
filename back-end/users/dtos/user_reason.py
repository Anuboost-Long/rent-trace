from rest_framework import serializers


class UserReasonDto(serializers.Serializer):
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Saved in the account's history. A default is used when left out.",
    )
