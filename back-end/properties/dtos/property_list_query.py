from rest_framework import serializers

from properties.models import PropertyStatus


class PropertyListQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Words to find in the name, address, or the owner's name or email.",
    )
    status = serializers.ChoiceField(choices=PropertyStatus.values, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 20."
    )
