from rest_framework import serializers

from accounts.resources.user_brief import UserBriefResource


class ActivityEntryResource(serializers.Serializer):
    action = serializers.CharField()
    person = UserBriefResource()
    by = UserBriefResource(allow_null=True)
    at = serializers.DateTimeField()
