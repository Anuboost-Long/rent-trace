from rest_framework import serializers

from properties.catalogue import UNIT_TYPES


class UnitFieldsDto(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    unit_number = serializers.CharField(
        max_length=50, required=False, allow_null=True, allow_blank=True
    )
    unit_type = serializers.ChoiceField(choices=UNIT_TYPES)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_public = serializers.BooleanField(required=False)
