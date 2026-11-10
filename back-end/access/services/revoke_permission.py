from django.db import transaction
from rest_framework.exceptions import NotFound

from access.services.shared import rules
from accounts.models import User, UserPermissionBridge
from accounts.services.shared import account_management as manage


def revoke_permission(*, actor, user_id, permission_code, reason=None):
    permission = rules.find_active_permission(permission_code)
    _attempt(actor, user_id, permission, reason)


@transaction.atomic
def _attempt(actor, user_id, permission, reason):
    target = User.objects.not_deleted().select_for_update().filter(pk=user_id).first()
    if target is None:
        raise NotFound("No user with this id.")
    manage.ensure_can_edit(actor, target)
    rules.ensure_may_change_grant(actor, target, permission)

    grant = (
        UserPermissionBridge.objects.active().for_user(target).filter(permission=permission).first()
    )
    if grant is None:
        return
    grant.is_active = False
    grant.updated_by = actor
    grant.row_version += 1
    grant.save()
    manage.record_change(
        actor=actor,
        target=target,
        action="ADMIN_REVOKED_PERMISSION",
        before={"permission": permission.code},
        after={},
        reason=reason,
    )
