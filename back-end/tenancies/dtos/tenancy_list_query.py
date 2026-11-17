from rest_framework import serializers

from tenancies.models import TenancyStatus


class TenancyListQueryDto(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Words in the reference, property, unit, or a tenant's name or email.",
    )
    status = serializers.ChoiceField(choices=TenancyStatus.values, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 20."
    )
