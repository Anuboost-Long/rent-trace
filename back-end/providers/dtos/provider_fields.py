from rest_framework import serializers

from providers.dtos.provider_property_link import ProviderPropertyLinkDto


class ProviderFieldsDto(serializers.Serializer):
    business_name = serializers.CharField(max_length=200)
    contact_name = serializers.CharField(
        max_length=150, required=False, allow_null=True, allow_blank=True
    )
    phone_number = serializers.CharField(
        max_length=30, required=False, allow_null=True, allow_blank=True
    )
    email = serializers.EmailField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )
    website = serializers.URLField(
        max_length=500, required=False, allow_null=True, allow_blank=True
    )
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    category_codes = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Codes from the service categories list, such as PLUMBING.",
    )
    properties = ProviderPropertyLinkDto(
        many=True,
        required=False,
        help_text="The landlord's properties this provider serves, and whether they are preferred.",
    )
