from rest_framework import serializers

from maintenance.models import MaintenancePriority


class ReportIssueDto(serializers.Serializer):
    tenancy_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=4000)
    priority = serializers.ChoiceField(choices=MaintenancePriority.values)
