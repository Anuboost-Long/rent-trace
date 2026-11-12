from rest_framework import serializers

from notifications.models import Notification


class NotificationResource(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "kind", "subject_id", "title", "body", "created_at", "read_at"]
