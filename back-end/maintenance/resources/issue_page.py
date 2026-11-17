from rest_framework import serializers

from maintenance.resources.issue_summary import IssueSummaryResource


class IssuePageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = IssueSummaryResource(many=True)
