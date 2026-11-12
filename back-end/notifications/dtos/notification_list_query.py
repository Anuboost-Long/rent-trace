from rest_framework import serializers


class NotificationListQueryDto(serializers.Serializer):
    unread = serializers.BooleanField(required=False, help_text="Only notifications not yet read.")
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 20."
    )
