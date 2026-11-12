from rest_framework import serializers

from tenancies.models import TenancyInvitation


class MyInvitationResource(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    unit_name = serializers.CharField(source="tenancy.property_unit.name")
    invited_by = serializers.SerializerMethodField()

    class Meta:
        model = TenancyInvitation
        fields = ["id", "property_name", "unit_name", "invited_by", "is_primary", "expires_at"]

    def get_property_name(self, invitation) -> str:
        place = invitation.tenancy.property_unit.property
        return place.property_name or f"{place.address_line_1}, {place.suburb}"

    def get_invited_by(self, invitation) -> str:
        sender = invitation.created_by
        return f"{sender.first_name} {sender.last_name}" if sender else ""
