from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from properties.services.shared.queries import live_properties
from reviews.models import ReviewKind, ReviewSubmissionFile

NOT_FOUND = "No photo with this id."


def open_evidence_photo(*, user, file_id, as_admin=False):
    """The author, a current owner of the property, or an admin; anyone else gets a 404."""
    link = (
        ReviewSubmissionFile.objects.filter(
            file_id=file_id, submission__request__kind=ReviewKind.EVIDENCE_REVIEW
        )
        .select_related("file", "submission__request__target__condition_record__property_unit")
        .first()
    )
    if link is None:
        raise NotFound(NOT_FOUND)
    request = link.submission.request
    place_id = request.target.condition_record.property_unit.property_id
    is_party = request.requested_by_id == user.pk or (
        live_properties(user).filter(pk=place_id).exists()
    )
    if not (as_admin or is_party):
        raise NotFound(NOT_FOUND)
    if not default_storage.exists(link.file.object_key):
        raise NotFound("This photo is no longer available.")
    return link.file, default_storage.open(link.file.object_key, "rb")
