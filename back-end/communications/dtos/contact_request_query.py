from rest_framework import serializers

from communications.models import ContactRequestStatus


class ContactRequestQueryDto(serializers.Serializer):
    status = serializers.ChoiceField(choices=ContactRequestStatus.values, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 20."
    )
