from django.utils import timezone
from rest_framework import serializers

from tenancies.models import TenancyInvitation
from tenancies.services.shared.invitations import invitation_status


class InvitationResource(serializers.ModelSerializer):
    email = serializers.CharField(source="email_normalized")
    status = serializers.SerializerMethodField()

    class Meta:
        model = TenancyInvitation
        fields = [
            "id",
            "email",
            "is_primary",
            "status",
            "expires_at",
            "created_at",
            "accepted_at",
            "revoked_at",
        ]

    def get_status(self, invitation) -> str:
        return invitation_status(invitation, timezone.now())
