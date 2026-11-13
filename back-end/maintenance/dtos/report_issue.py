from rest_framework import serializers

from maintenance.models import MaintenancePriority


class ReportIssueDto(serializers.Serializer):
    tenancy_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=4000)
    priority = serializers.ChoiceField(choices=MaintenancePriority.values)
    category_code = serializers.CharField(
        max_length=50,
        required=False,
        allow_null=True,
        help_text="The kind of problem, from the service categories list, such as PLUMBING.",
    )
