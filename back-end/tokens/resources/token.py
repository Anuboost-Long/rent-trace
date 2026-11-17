from django.utils import timezone
from rest_framework import serializers

from accounts.models import AuthSession
from accounts.resources.user_brief import UserBriefResource


class TokenResource(serializers.ModelSerializer):
    user = UserBriefResource()
    status = serializers.SerializerMethodField()
    mfa_verified = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = AuthSession
        fields = [
            "id",
            "user",
            "device_name",
            "user_agent",
            "ip_address",
            "verified_method",
            "status",
            "mfa_verified",
            "is_current",
            "created_at",
            "last_used_at",
            "expires_at",
            "revoked_at",
        ]

    def get_status(self, session) -> str:
        if session.revoked_at is not None:
            return "REVOKED"
        return "EXPIRED" if session.expires_at <= timezone.now() else "ACTIVE"

    def get_mfa_verified(self, session) -> bool:
        return session.mfa_verified_at is not None

    def get_is_current(self, session) -> bool:
        current = self.context.get("current_session")
        return current is not None and current.pk == session.pk
