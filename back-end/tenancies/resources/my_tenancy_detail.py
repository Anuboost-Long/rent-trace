from rest_framework import serializers

from conditions.resources import TenantConditionResource
from tenancies.models import TermChangeStatus
from tenancies.resources.housemate_request import HousemateRequestResource
from tenancies.resources.my_tenancy import MyTenancyResource
from tenancies.resources.term_change import MyTermChangeResource


class MyTenancyDetailResource(MyTenancyResource):
    housemates = serializers.SerializerMethodField(help_text="Other current tenants, names only.")
    housemate_requests = HousemateRequestResource(
        source="my_requests", many=True, help_text="Only the requests this tenant made."
    )

    unit_conditions = TenantConditionResource(
        source="property_unit.shown_conditions",
        many=True,
        help_text="Condition notes the landlord chose to show tenants of this unit.",
    )
    pending_change = serializers.SerializerMethodField(
        help_text="A rent or bond increase waiting for your answer, or null."
    )
    term_history = serializers.SerializerMethodField(
        help_text="Rent and bond changes that took effect."
    )

    class Meta(MyTenancyResource.Meta):
        fields = [
            *MyTenancyResource.Meta.fields,
            "housemates",
            "housemate_requests",
            "unit_conditions",
            "pending_change",
            "term_history",
        ]

    def get_housemates(self, tenancy) -> list[dict]:
        return [
            {
                "first_name": party.tenant.first_name,
                "last_name": party.tenant.last_name,
                "is_primary": party.is_primary,
            }
            for party in tenancy.housemates
        ]

    def _people_context(self, tenancy):
        me = tenancy.my_parties[0].tenant
        people = [{"user_id": me.pk, "name": f"{me.first_name} {me.last_name} (you)"}]
        people += [
            {
                "user_id": party.tenant_id,
                "name": f"{party.tenant.first_name} {party.tenant.last_name}",
            }
            for party in tenancy.housemates
        ]
        return {"people": people, "me_id": me.pk}

    def get_pending_change(self, tenancy) -> dict | None:
        pending = next(
            (c for c in tenancy.visible_term_changes if c.status == TermChangeStatus.PENDING), None
        )
        if pending is None:
            return None
        return MyTermChangeResource(pending, context=self._people_context(tenancy)).data

    def get_term_history(self, tenancy) -> list[dict]:
        applied = [c for c in tenancy.visible_term_changes if c.status == TermChangeStatus.APPLIED]
        return MyTermChangeResource(
            applied[:20], many=True, context=self._people_context(tenancy)
        ).data
