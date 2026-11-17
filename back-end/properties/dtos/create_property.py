from rest_framework import serializers

from properties.dtos.property_fields import PropertyFieldsDto


class CreatePropertyDto(PropertyFieldsDto):
    owner_id = serializers.IntegerField(help_text="The landlord who owns the property.")
