from rest_framework import serializers

from reviews.resources.correction import CorrectionResource


class CorrectionPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = CorrectionResource(many=True)
