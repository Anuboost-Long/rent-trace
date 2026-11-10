from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.models import AuthSession
from accounts.services.shared import account_management as manage

IS_CURRENT = "This is the session you are using right now. Sign out instead."


def revoke_token(*, actor, current_session, token_id, reason=None):
    if current_session.pk == token_id:
        raise ValidationError(IS_CURRENT)
    _attempt(actor, token_id, reason)
    return AuthSession.objects.with_user().get(pk=token_id)


@transaction.atomic
def _attempt(actor, token_id, reason):
    now = timezone.now()
    session = (
        AuthSession.objects.select_for_update(of=("self",)).with_user().filter(pk=token_id).first()
    )
    if session is None:
        raise NotFound("No session with this id.")
    manage.ensure_can_edit(actor, session.user)
    if session.revoked_at is not None or session.expires_at <= now:
        return
    session.revoked_at = now
    session.save()
    manage.record_change(
        actor=actor,
        target=session.user,
        action="ADMIN_REVOKED_SESSION",
        before={"session": session.pk},
        after={"device_name": session.device_name, "revoked": True},
        reason=reason,
    )
