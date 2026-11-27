import uuid

from reviews.models import (
    RemovalEffect,
    RemovalEffectType,
    ReviewSubmissionFile,
    ReviewTarget,
)
from reviews.services.shared.history import record_change


def _hide(row, admin, now):
    row.deleted_at = now
    row.deleted_by = admin
    row.updated_by = admin
    row.row_version += 1
    row.save()


def _effect(request, target, effect, reason, admin):
    RemovalEffect.objects.create(
        request=request,
        target=target,
        effect=effect,
        reason=reason,
        created_by=admin,
        correlation_id=uuid.uuid4(),
    )


def _target_for(admin, **link):
    audit = {"created_by": admin, "correlation_id": uuid.uuid4()}
    return ReviewTarget.objects.get_or_create(**link, defaults=audit)[0]


def apply_removal(request, admin, reason, now):
    """Hides each record and, when asked, what hangs off it. Nothing is deleted."""
    for item in request.removal_items.all():
        record = item.target.condition_record
        _hide(record, admin, now)
        _effect(request, item.target, RemovalEffectType.HIDE_RECORD, reason, admin)
        record_change(
            request,
            admin,
            "HIDE_RECORD",
            {"hidden": False},
            {"hidden": True},
            reason,
            target=item.target,
        )
        if item.include_descendants:
            _hide_descendants(request, item, record, admin, reason, now)


def _hide_descendants(request, item, record, admin, reason, now):
    for related in record.related_records.filter(deleted_at__isnull=True):
        _hide(related, admin, now)
        target = _target_for(admin, condition_record=related)
        _effect(request, target, RemovalEffectType.HIDE_DESCENDANTS, reason, admin)
    attached = ReviewSubmissionFile.objects.filter(
        submission__request__target=item.target, file__deleted_at__isnull=True
    ).select_related("file")
    for link in attached:
        _hide(link.file, admin, now)
        target = _target_for(admin, file=link.file)
        _effect(request, target, RemovalEffectType.HIDE_FILE, reason, admin)
