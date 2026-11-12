from rest_framework import serializers

from maintenance.models import MaintenanceStatus


class IssueListQueryDto(serializers.Serializer):
    status = serializers.ChoiceField(choices=MaintenanceStatus.values, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 20."
    )
