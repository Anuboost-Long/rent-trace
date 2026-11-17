from rest_framework import serializers


class ProviderListQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False, help_text="Words in the business name or contact name."
    )
    category = serializers.CharField(
        required=False, help_text="A service category code, such as PLUMBING."
    )
