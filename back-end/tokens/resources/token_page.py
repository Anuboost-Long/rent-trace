from rest_framework import serializers

from tokens.resources.token import TokenResource


class TokenPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = TokenResource(many=True)
