from django.utils import timezone
from rest_framework import serializers

from tenancies.models import TenancyInvitation
from tenancies.services.shared.invitations import invitation_status, waiting_on


class InvitationResource(serializers.ModelSerializer):
    email = serializers.CharField(source="email_normalized")
    status = serializers.SerializerMethodField()
    waiting_on = serializers.SerializerMethodField(
        help_text="Who still has to say yes: LANDLORD and/or INVITEE. Empty once it is over."
    )
    requested_by = serializers.SerializerMethodField(help_text="The tenant who asked, if one did.")

    class Meta:
        model = TenancyInvitation
        fields = [
            "id",
            "email",
            "is_primary",
            "status",
            "requested_by_tenant",
            "requested_by",
            "landlord_decision",
            "invitee_accepted_at",
            "waiting_on",
            "expires_at",
            "created_at",
            "accepted_at",
            "revoked_at",
        ]

    def get_status(self, invitation) -> str:
        return invitation_status(invitation, timezone.now())

    def get_waiting_on(self, invitation) -> list[str]:
        return waiting_on(invitation, timezone.now())

    def get_requested_by(self, invitation) -> str | None:
        asker = invitation.created_by
        if not invitation.requested_by_tenant or asker is None:
            return None
        return f"{asker.first_name} {asker.last_name}"
