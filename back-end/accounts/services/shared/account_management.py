import uuid

from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from accounts.models import AccountAccessHistory, User
from accounts.services.shared.account_rules import is_admin_side
from accounts.services.shared.permissions import granted_codes
from accounts.services.shared.privileges import CANT_ACT_ON_MORE_POWERFUL, ensure_holds


def find_user_for_update(user_id):
    user = User.objects.not_deleted().select_for_update().filter(pk=user_id).first()
    if user is None:
        raise NotFound("No user with this id.")
    return user


def ensure_can_edit(actor, target):
    if is_admin_side(target):
        ensure_holds(actor, granted_codes(target), CANT_ACT_ON_MORE_POWERFUL)


def ensure_can_remove(actor, target, verb):
    ensure_can_edit(actor, target)
    if target.pk == actor.pk:
        raise ValidationError(f"You can't {verb} your own account.")
    if target.is_top_level_admin:
        raise PermissionDenied(f"The super admin account can't be {verb}d.")


def save_change(actor, target, now):
    target.updated_by = actor
    target.updated_at = now
    target.row_version += 1
    target.save()


def record_change(*, actor, target, action, before, after, reason):
    AccountAccessHistory.objects.create(
        user=target,
        action=action,
        before_values=before,
        after_values=after,
        reason=reason or f"{action} by admin {actor.pk}",
        correlation_id=uuid.uuid4(),
        created_by=actor,
    )


def now():
    return timezone.now()
