from rest_framework import serializers

from reviews.resources.removal import RemovalResource


class RemovalPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = RemovalResource(many=True)
