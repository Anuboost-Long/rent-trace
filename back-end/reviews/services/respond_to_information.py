import uuid

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from conditions.models import ConditionVersion, SourceType
from properties.services.shared.queries import current_owner_users
from reviews.models import ReviewStatus, ReviewSubmission, ReviewSubmissionFile
from reviews.services.shared import notices
from reviews.services.shared.decisions import move, require_awaiting_reply
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_wrote, reloaded


@transaction.atomic
def respond_to_information(*, user, request_id, message, changes):
    request = find_evidence_I_wrote(user, request_id, lock=True)
    require_awaiting_reply(request)
    now = timezone.now()
    message = message.strip()
    earlier = request.current_submission
    note = request.target.condition_record
    version = _next_version(note, earlier.proposed_condition_version, changes, user, now)
    revision_no = request.submissions.aggregate(last=Max("revision_no"))["last"] + 1
    submission = ReviewSubmission.objects.create(
        request=request,
        revision_no=revision_no,
        submitted_by=user,
        expected_row_version=note.row_version,
        base_condition_version=earlier.proposed_condition_version,
        proposed_condition_version=version,
        proposed_values={
            "title": version.title,
            "description": version.condition_description,
            "observed_at": version.observed_at.isoformat(),
        },
        reason=message,
        created_by=user,
        correlation_id=uuid.uuid4(),
    )
    for link in earlier.files.all():
        ReviewSubmissionFile.objects.create(submission=submission, file=link.file, created_by=user)
    request.current_submission = submission
    request.submitted_at = now
    move(request, ReviewStatus.PENDING_REVIEW, user)
    record_transition(
        request,
        ReviewStatus.PENDING_REVIEW,
        "RESPOND",
        user,
        message,
        from_status=ReviewStatus.NEEDS_INFORMATION,
        submission=submission,
    )
    place = note.property_unit.property
    notices.information_provided(request, user, current_owner_users(place), version.title, message)
    return reloaded(request)


def _next_version(note, earlier, changes, user, now):
    last = note.versions.aggregate(last=Max("version_no"))["last"]
    return ConditionVersion.objects.create(
        condition_record=note,
        version_no=last + 1,
        supersedes_version=earlier,
        title=changes.get("title") or earlier.title,
        condition_description=(
            changes["description"] or None
            if "description" in changes
            else earlier.condition_description
        ),
        source_type=SourceType.TENANT,
        observed_at=changes.get("observed_at") or earlier.observed_at,
        submitted_by=user,
        submitted_at=now,
        created_by=user,
        correlation_id=uuid.uuid4(),
    )
