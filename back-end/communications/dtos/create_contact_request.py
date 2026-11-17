from rest_framework import serializers


class CreateContactRequestDto(serializers.Serializer):
    listing_id = serializers.IntegerField(help_text="The listed property's id.")
    unit_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(max_length=1000)
