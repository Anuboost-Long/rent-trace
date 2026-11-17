from rest_framework import serializers

from bans.resources.ban import BanResource


class BanPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = BanResource(many=True)
