from rest_framework import serializers


class UpdateProviderLinkDto(serializers.Serializer):
    is_recommended = serializers.BooleanField(required=False)
    contract_notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
