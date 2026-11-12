from rest_framework import serializers

from listings.resources.listing_summary import ListingSummaryResource


class ListingPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = ListingSummaryResource(many=True)
