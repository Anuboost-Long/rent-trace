from rest_framework.exceptions import NotFound

from reviews.models import ReviewRequest, ReviewStatus
from reviews.services.shared.scope import find_my_unit
from tenancies.models import TenancyParty


def list_corrections_for_tenancy(*, tenant, tenancy_id):
    is_member = TenancyParty.objects.filter(tenancy_id=tenancy_id, tenant=tenant).exists()
    if not is_member:
        raise NotFound("No tenancy with this id.")
    mine = ReviewRequest.objects.corrections().filter(scopes__tenancy_id=tenancy_id)
    return mine.filter(requested_by=tenant).with_correction_details().order_by("-id")


def list_corrections_for_unit(*, landlord, unit_id):
    find_my_unit(landlord, unit_id)
    on_unit = ReviewRequest.objects.corrections().filter(
        target__condition_record__property_unit_id=unit_id
    )
    return on_unit.with_correction_details().order_by("-id")


def list_correction_queue(*, status=None):
    waiting = ReviewRequest.objects.corrections().filter(
        status=status or ReviewStatus.PENDING_REVIEW
    )
    return waiting.with_correction_details().order_by("submitted_at", "id")
