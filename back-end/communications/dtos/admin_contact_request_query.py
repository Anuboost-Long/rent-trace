from rest_framework import serializers

from communications.dtos.contact_request_query import ContactRequestQueryDto


class AdminContactRequestQueryDto(ContactRequestQueryDto):
    q = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Matches the property name, suburb or the tenant's name.",
    )
