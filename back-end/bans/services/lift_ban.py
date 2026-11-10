from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.models import Ban, BanType
from accounts.services.shared import account_management as manage


def lift_ban(*, actor, ban_id, reason):
    _attempt(actor, ban_id, reason.strip())
    return Ban.objects.with_people().get(pk=ban_id)


@transaction.atomic
def _attempt(actor, ban_id, reason):
    now = timezone.now()
    ban = Ban.objects.select_for_update(of=("self",)).with_people().filter(pk=ban_id).first()
    if ban is None:
        raise NotFound("No ban with this id.")
    if ban.lifted_at is not None or (ban.expires_at is not None and ban.expires_at <= now):
        raise ValidationError("This ban has already ended.")
    if ban.ban_type == BanType.ACCOUNT:
        manage.ensure_can_edit(actor, ban.user)

    ban.lifted_at, ban.lifted_by, ban.lift_reason = now, actor, reason
    ban.updated_by = actor
    ban.row_version += 1
    ban.save()
    if ban.ban_type == BanType.ACCOUNT:
        manage.record_change(
            actor=actor,
            target=ban.user,
            action="ADMIN_LIFTED_BAN",
            before={"ban": ban.pk},
            after={"lifted": True},
            reason=reason,
        )
