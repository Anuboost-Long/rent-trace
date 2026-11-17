from rest_framework import serializers

from properties.dtos.property_fields import PropertyFieldsDto
from properties.models import PropertyStatus


class UpdatePropertyDto(PropertyFieldsDto):
    property_status = serializers.ChoiceField(choices=PropertyStatus.values, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, partial=True, **kwargs)
