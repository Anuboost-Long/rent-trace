from django.utils import timezone
from rest_framework import serializers

from accounts.models import Ban
from accounts.resources.user_brief import UserBriefResource


class BanResource(serializers.ModelSerializer):
    user = UserBriefResource(allow_null=True)
    created_by = UserBriefResource(allow_null=True)
    lifted_by = UserBriefResource(allow_null=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Ban
        fields = [
            "id",
            "ban_type",
            "value",
            "user",
            "reason",
            "status",
            "created_at",
            "created_by",
            "expires_at",
            "lifted_at",
            "lifted_by",
            "lift_reason",
        ]

    def get_status(self, ban) -> str:
        if ban.lifted_at is not None:
            return "LIFTED"
        if ban.expires_at is not None and ban.expires_at <= timezone.now():
            return "EXPIRED"
        return "ACTIVE"
