from rest_framework import serializers

from providers.resources.service_provider import ServiceProviderResource


class ProviderPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = ServiceProviderResource(many=True)
