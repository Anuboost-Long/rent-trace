from django.db.models import Prefetch

from conditions.models import ConditionRecord, ConditionRecordType
from properties.models import PropertyOwner
from tenancies.models import (
    Tenancy,
    TenancyInvitation,
    TenancyParty,
    TenancyTermChange,
    TermChangeStatus,
)


def my_tenancies(user):
    """Every tenancy the person has joined, past ones included, newest start first."""
    mine = (
        TenancyParty.objects.filter(tenant=user, deleted_at__isnull=True)
        .select_related("tenant")
        .order_by("-id")
    )
    housemates = TenancyParty.objects.current().exclude(tenant=user).select_related("tenant")
    owners = (
        PropertyOwner.objects.filter(valid_to__isnull=True, deleted_at__isnull=True)
        .select_related("owner")
        .order_by("-is_primary_owner", "id")
    )
    return (
        Tenancy.objects.live()
        .for_tenant(user)
        .select_related("property_unit__property")
        .prefetch_related(
            Prefetch("parties", queryset=mine, to_attr="my_parties"),
            Prefetch(
                "term_changes",
                queryset=TenancyTermChange.objects.filter(
                    status__in=[TermChangeStatus.PENDING, TermChangeStatus.APPLIED]
                )
                .select_related("created_by")
                .prefetch_related("decisions")
                .order_by("-created_at", "-id"),
                to_attr="visible_term_changes",
            ),
            Prefetch("parties", queryset=housemates.order_by("id"), to_attr="housemates"),
            Prefetch(
                "property_unit__condition_records",
                queryset=ConditionRecord.objects.filter(
                    record_type=ConditionRecordType.BASELINE,
                    is_shown_to_tenants=True,
                    deleted_at__isnull=True,
                )
                .select_related("accepted_version")
                .order_by("id"),
                to_attr="shown_conditions",
            ),
            Prefetch("property_unit__property__owners", queryset=owners, to_attr="current_owners"),
            Prefetch(
                "invitations",
                queryset=TenancyInvitation.objects.not_deleted()
                .filter(requested_by_tenant=True, created_by=user)
                .order_by("-id"),
                to_attr="my_requests",
            ),
        )
        .order_by("-start_date", "-id")
    )
