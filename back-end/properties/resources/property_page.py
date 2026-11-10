from rest_framework import serializers

from properties.resources.property_summary import PropertySummaryResource


class PropertyPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = PropertySummaryResource(many=True)
