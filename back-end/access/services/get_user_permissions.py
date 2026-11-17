from django.utils import timezone

from accounts.models import Permission, UserPermissionBridge
from accounts.services.shared.permissions import permission_codes
from accounts.services.shared.roles import effective_role_ids
from users.services.get_user import get_user


def get_user_permissions(*, user_id):
    user = get_user(user_id=user_id)
    through_roles = [
        {"code": permission.code, "name": permission.name, "module": permission.module}
        for permission in Permission.objects.granted_to_roles(effective_role_ids(user)).order_by(
            "module", "code"
        )
    ]
    grants = (
        UserPermissionBridge.objects.for_user(user)
        .select_related("permission")
        .order_by("permission__module", "permission__code")
    )
    return {
        "roles": sorted(bridge.role.name for bridge in user.active_role_bridges),
        "through_roles": through_roles,
        "grants": list(grants),
        "effective": sorted(permission_codes(user, timezone.now())),
    }
