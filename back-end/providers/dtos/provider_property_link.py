from rest_framework import serializers


class ProviderPropertyLinkDto(serializers.Serializer):
    property_id = serializers.IntegerField(min_value=1)
    is_recommended = serializers.BooleanField(required=False, default=False)
    contract_notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
