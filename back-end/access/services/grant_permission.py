from django.db import transaction
from rest_framework.exceptions import NotFound

from access.services.shared import rules
from accounts.models import User, UserPermissionBridge
from accounts.services.shared import account_management as manage


def grant_permission(*, actor, user_id, permission_code, reason):
    permission = rules.find_active_permission(permission_code)
    _attempt(actor, user_id, permission, reason.strip())


@transaction.atomic
def _attempt(actor, user_id, permission, reason):
    target = User.objects.not_deleted().select_for_update().filter(pk=user_id).first()
    if target is None:
        raise NotFound("No user with this id.")
    manage.ensure_can_edit(actor, target)
    rules.ensure_may_change_grant(actor, target, permission)
    rules.ensure_may_receive(target, permission)

    grant, created = UserPermissionBridge.objects.get_or_create(
        user=target,
        permission=permission,
        defaults={"reason": reason, "created_by": actor},
    )
    if not created and grant.is_active:
        return
    if not created:
        grant.is_active = True
        grant.reason = reason
        grant.updated_by = actor
        grant.row_version += 1
        grant.save()
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_GRANTED_PERMISSION",
        before={},
        after={"permission": permission.code},
        reason=reason,
    )
