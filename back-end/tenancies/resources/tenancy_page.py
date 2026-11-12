from rest_framework import serializers

from tenancies.resources.tenancy_summary import TenancySummaryResource


class TenancyPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = TenancySummaryResource(many=True)
