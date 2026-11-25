from rest_framework import serializers

from reviews.resources.case import CaseResource


class CasePageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = CaseResource(many=True)
