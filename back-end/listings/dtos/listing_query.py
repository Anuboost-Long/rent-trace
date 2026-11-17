from rest_framework import serializers

from locations.catalogue import STATE_CODES
from properties.catalogue import PROPERTY_TYPES

SORTS = ["newest", "rent_low", "rent_high"]


class ListingQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Words to find in the name, suburb, postcode or description.",
    )
    state = serializers.ChoiceField(choices=STATE_CODES, required=False)
    suburb = serializers.CharField(required=False, max_length=100)
    type = serializers.ChoiceField(choices=PROPERTY_TYPES, required=False)
    min_rent = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, help_text="Per week."
    )
    max_rent = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, help_text="Per week."
    )
    sort = serializers.ChoiceField(choices=SORTS, required=False, default="newest")
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=48, help_text="Up to 48. Default 20."
    )
