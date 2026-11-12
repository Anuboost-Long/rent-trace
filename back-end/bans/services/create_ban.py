from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from accounts.models import Ban, BanType
from accounts.services.shared import account_management as manage
from accounts.services.shared.sessions import revoke_sessions

ALREADY_BANNED = "This is already banned."


def create_ban(*, actor, ban_type, reason, value=None, user_id=None, expires_at=None):
    try:
        ban = _attempt(actor, ban_type, reason.strip(), value, user_id, expires_at)
    except IntegrityError as error:
        raise ValidationError(ALREADY_BANNED) from error
    return Ban.objects.with_people().get(pk=ban.pk)


@transaction.atomic
def _attempt(actor, ban_type, reason, value, user_id, expires_at):
    now = manage.now()
    target = None
    if ban_type == BanType.ACCOUNT:
        target = manage.find_user_for_update(user_id)
        manage.ensure_can_remove(actor, target, "ban")
    ban = Ban.objects.create(
        ban_type=ban_type,
        value=value,
        user=target,
        reason=reason,
        expires_at=expires_at,
        created_by=actor,
        updated_by=actor,
    )
    if target:
        revoke_sessions(target, now)
        manage.record_change(
            actor=actor,
            target=target,
            action="ADMIN_BANNED_ACCOUNT",
            before={"banned": False},
            after={"ban": ban.pk, "expires_at": expires_at and expires_at.isoformat()},
            reason=reason,
        )
    return ban
