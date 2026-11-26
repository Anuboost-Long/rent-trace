from rest_framework.exceptions import NotFound

from properties.models import PropertyUnit
from properties.services.shared.queries import live_properties
from reviews.models import ReviewRequest

NOT_FOUND = "No condition evidence with this id."


def find_my_unit(user, unit_id):
    unit = PropertyUnit.objects.filter(
        pk=unit_id, property__in=live_properties(user), deleted_at__isnull=True
    ).first()
    if unit is None:
        raise NotFound("No unit with this id.")
    return unit


def _locked(requests, lock):
    return requests.select_for_update(of=("self",)) if lock else requests


def find_evidence_I_answer(user, request_id, *, lock=False):
    """404 unless it is evidence about a unit on a property the person owns today."""
    requests = ReviewRequest.objects.evidence().on_properties(live_properties(user))
    found = _locked(requests.with_details(), lock).filter(pk=request_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


def find_evidence_I_wrote(user, request_id, *, lock=False):
    requests = ReviewRequest.objects.evidence().filter(requested_by=user)
    found = _locked(requests.with_details(), lock).filter(pk=request_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


def find_evidence_I_am_party_to(user, request_id, *, lock=False):
    """The author or a current owner; 404 for anyone else."""
    try:
        return find_evidence_I_wrote(user, request_id, lock=lock)
    except NotFound:
        return find_evidence_I_answer(user, request_id, lock=lock)


def reloaded(request):
    return ReviewRequest.objects.with_details().get(pk=request.pk)
