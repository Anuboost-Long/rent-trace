from django.utils import timezone
from rest_framework import serializers

from tenancies.models import TenancyInvitation
from tenancies.services.shared.invitations import waiting_on


class MyInvitationResource(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    unit_name = serializers.CharField(source="tenancy.property_unit.name")
    invited_by = serializers.SerializerMethodField()
    joined = serializers.SerializerMethodField(help_text="True once they are a tenant of it.")
    waiting_on = serializers.SerializerMethodField(help_text="LANDLORD and/or INVITEE.")

    class Meta:
        model = TenancyInvitation
        fields = [
            "id",
            "property_name",
            "unit_name",
            "invited_by",
            "is_primary",
            "requested_by_tenant",
            "joined",
            "waiting_on",
            "expires_at",
        ]

    def get_property_name(self, invitation) -> str:
        place = invitation.tenancy.property_unit.property
        return place.property_name or f"{place.address_line_1}, {place.suburb}"

    def get_joined(self, invitation) -> bool:
        return invitation.accepted_at is not None

    def get_waiting_on(self, invitation) -> list[str]:
        return waiting_on(invitation, timezone.now())

    def get_invited_by(self, invitation) -> str:
        sender = invitation.created_by
        return f"{sender.first_name} {sender.last_name}" if sender else ""
