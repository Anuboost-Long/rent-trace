from django.utils import timezone
from rest_framework import serializers

from tenancies.models import TenancyInvitation
from tenancies.services.shared.invitations import invitation_status, waiting_on


class HousemateRequestResource(serializers.ModelSerializer):
    """A tenant's own request, seen by that tenant; it carries the email they typed."""

    email = serializers.CharField(source="email_normalized")
    status = serializers.SerializerMethodField()
    waiting_on = serializers.SerializerMethodField()

    class Meta:
        model = TenancyInvitation
        fields = ["id", "email", "status", "waiting_on", "created_at", "expires_at"]

    def get_status(self, invitation) -> str:
        return invitation_status(invitation, timezone.now())

    def get_waiting_on(self, invitation) -> list[str]:
        return waiting_on(invitation, timezone.now())
