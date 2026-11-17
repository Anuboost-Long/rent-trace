from access.services.list_permissions import find_listed_permission
from accounts.models import Role, RolePermissionBridge, User, UserPermissionBridge
from accounts.services.shared.roles import descendant_role_ids


def get_permission_holders(*, code):
    permission = find_listed_permission(code)
    direct_ids = set(
        RolePermissionBridge.objects.active()
        .filter(permission=permission, role__is_active=True)
        .values_list("role_id", flat=True)
    )
    all_ids = descendant_role_ids(direct_ids)
    roles = [
        {"code": role.code, "name": role.name, "inherited": role.pk not in direct_ids}
        for role in Role.objects.filter(pk__in=all_ids).order_by("code")
    ]
    grants = (
        UserPermissionBridge.objects.active()
        .for_permission(permission)
        .filter(user__deleted_at__isnull=True)
        .select_related("user", "created_by", "updated_by")
        .newest_first()
    )
    return {
        "permission": permission,
        "roles": roles,
        "people_through_roles": User.objects.not_deleted().with_any_role(all_ids).count(),
        "grants": list(grants),
    }
