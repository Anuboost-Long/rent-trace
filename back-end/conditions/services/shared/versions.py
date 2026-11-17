import uuid

from django.utils import timezone

from conditions.models import ConditionVersion, SourceType


def add_version(note, actor, *, title, description, observed_at):
    previous = note.accepted_version
    version = ConditionVersion.objects.create(
        condition_record=note,
        version_no=previous.version_no + 1 if previous else 1,
        supersedes_version=previous,
        title=title,
        condition_description=description,
        source_type=SourceType.LANDLORD,
        observed_at=observed_at,
        submitted_by=actor,
        submitted_at=timezone.now(),
        created_by=actor,
        correlation_id=uuid.uuid4(),
    )
    note.accepted_version = version
    return version
