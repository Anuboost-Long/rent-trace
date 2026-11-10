from rest_framework import serializers

from locations.catalogue import STATE_CODES
from properties.catalogue import PROPERTY_TYPES


class PropertyFieldsDto(serializers.Serializer):
    property_name = serializers.CharField(
        max_length=150, required=False, allow_null=True, allow_blank=True
    )
    address_line_1 = serializers.CharField(max_length=255)
    address_line_2 = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )
    suburb = serializers.CharField(max_length=100)
    state = serializers.ChoiceField(choices=STATE_CODES)
    postcode = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=100, required=False)
    property_type = serializers.ChoiceField(choices=PROPERTY_TYPES)
    public_description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    private_notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
