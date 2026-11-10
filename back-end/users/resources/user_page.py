from rest_framework import serializers

from users.resources.user_summary import UserSummaryResource


class UserPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = UserSummaryResource(many=True)
