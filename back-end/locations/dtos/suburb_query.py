from rest_framework import serializers

from locations.catalogue import STATE_CODES


class SuburbQueryDto(serializers.Serializer):
    state = serializers.ChoiceField(choices=STATE_CODES)
    q = serializers.CharField(
        required=False, max_length=100, help_text="Words to find in the suburb name."
    )
    limit = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 50."
    )
