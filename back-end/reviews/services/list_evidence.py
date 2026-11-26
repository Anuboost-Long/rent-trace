from rest_framework.exceptions import NotFound

from reviews.models import ReviewRequest
from reviews.services.shared.scope import find_my_unit
from tenancies.models import TenancyParty


def list_evidence_for_unit(*, landlord, unit_id):
    find_my_unit(landlord, unit_id)
    return ReviewRequest.objects.evidence().on_unit(unit_id).with_details().order_by("-id")


def list_my_evidence(*, tenant, tenancy_id):
    is_member = TenancyParty.objects.filter(tenancy_id=tenancy_id, tenant=tenant).exists()
    if not is_member:
        raise NotFound("No tenancy with this id.")
    mine = ReviewRequest.objects.evidence().in_tenancy(tenancy_id).filter(requested_by=tenant)
    return mine.with_details().order_by("-id")


def list_evidence_for_admin(*, unit_id):
    return ReviewRequest.objects.evidence().on_unit(unit_id).with_details().order_by("-id")
