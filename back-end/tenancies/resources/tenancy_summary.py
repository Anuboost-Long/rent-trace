from django.utils import timezone
from rest_framework import serializers

from tenancies.models import Tenancy
from tenancies.services.shared.invitations import invitation_status


class TenancySummaryResource(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    property = serializers.SerializerMethodField()
    tenant_count = serializers.SerializerMethodField()
    pending_invitations = serializers.SerializerMethodField()

    class Meta:
        model = Tenancy
        fields = [
            "id",
            "reference_no",
            "status",
            "start_date",
            "end_date",
            "unit",
            "property",
            "tenant_count",
            "pending_invitations",
        ]

    def get_unit(self, tenancy) -> dict:
        unit = tenancy.property_unit
        return {"id": unit.pk, "name": unit.name}

    def get_property(self, tenancy) -> dict:
        place = tenancy.property_unit.property
        return {"id": place.pk, "name": place.property_name, "suburb": place.suburb}

    def get_tenant_count(self, tenancy) -> int:
        return len(tenancy.current_parties)

    def get_pending_invitations(self, tenancy) -> int:
        now = timezone.now()
        return sum(
            invitation_status(invitation, now) == "PENDING"
            for invitation in tenancy.all_invitations
        )
