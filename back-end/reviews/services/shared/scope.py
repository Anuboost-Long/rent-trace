from rest_framework.exceptions import NotFound

from conditions.models import ConditionRecord, ConditionRecordType
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


def find_evidence_I_answer(user, request_id, *, lock=False, as_admin=False):
    """404 unless it is evidence about a unit on a property the person owns today.
    A super admin acting for the owner may open any report."""
    evidence = ReviewRequest.objects.evidence()
    requests = evidence if as_admin else evidence.on_properties(live_properties(user))
    found = _locked(requests.with_details(), lock).filter(pk=request_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


def find_evidence_I_wrote(user, request_id, *, lock=False, as_admin=False):
    evidence = ReviewRequest.objects.evidence()
    requests = evidence if as_admin else evidence.filter(requested_by=user)
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


NO_NOTE = "No condition note with this id."
NO_CORRECTION = "No correction with this id."


def find_note_tenant_may_correct(unit, record_id):
    found = ConditionRecord.objects.filter(
        pk=record_id,
        property_unit=unit,
        record_type=ConditionRecordType.BASELINE,
        is_shown_to_tenants=True,
        deleted_at__isnull=True,
    ).first()
    if found is None:
        raise NotFound(NO_NOTE)
    return found


def find_note_landlord_may_correct(user, record_id):
    found = (
        ConditionRecord.objects.filter(
            pk=record_id,
            property_unit__property__in=live_properties(user),
            record_type=ConditionRecordType.DISCREPANCY,
            accepted_version__isnull=False,
            deleted_at__isnull=True,
        )
        .select_related("property_unit__property")
        .first()
    )
    if found is None:
        raise NotFound(NO_NOTE)
    return found


def find_correction_I_asked(user, request_id, *, lock=False):
    requests = ReviewRequest.objects.corrections().filter(requested_by=user)
    found = _locked(requests.with_correction_details(), lock).filter(pk=request_id).first()
    if found is None:
        raise NotFound(NO_CORRECTION)
    return found


def find_correction_for_admin(request_id, *, lock=False):
    requests = _locked(ReviewRequest.objects.corrections().with_correction_details(), lock)
    found = requests.filter(pk=request_id).first()
    if found is None:
        raise NotFound(NO_CORRECTION)
    return found


def reloaded_correction(request):
    return ReviewRequest.objects.with_correction_details().get(pk=request.pk)
