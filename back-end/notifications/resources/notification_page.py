from rest_framework import serializers

from notifications.resources.notification import NotificationResource


class NotificationPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = NotificationResource(many=True)
