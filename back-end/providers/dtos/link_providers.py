from rest_framework import serializers


class LinkProvidersDto(serializers.Serializer):
    provider_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text="Saved tradespeople to link to the property. Ones already linked are skipped.",
    )
