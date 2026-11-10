from accounts.models import UserPermissionBridge


def list_grants(*, q=None, permission_code=None):
    grants = (
        UserPermissionBridge.objects.active()
        .filter(user__deleted_at__isnull=True)
        .select_related("user", "permission", "created_by", "updated_by")
    )
    for term in (q or "").split():
        grants = grants.filter_user_text(term)
    if permission_code:
        grants = grants.filter(permission__code=permission_code)
    return grants.newest_first()
