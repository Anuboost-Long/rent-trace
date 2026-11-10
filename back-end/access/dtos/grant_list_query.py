from rest_framework import serializers


class GrantListQueryDto(serializers.Serializer):
    q = serializers.CharField(required=False, max_length=100, help_text="Name or email.")
    permission = serializers.CharField(
        required=False, max_length=100, help_text="A permission code."
    )
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
