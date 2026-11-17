from accounts.models import AccessPolicy, HiddenRecordsMode, Permission, UserPermissionBridge
from accounts.services.shared.account_rules import is_account_usable
from accounts.services.shared.roles import effective_role_ids, role_permission_codes

HIDDEN_RECORDS = "access.view_hidden_records"


def _may_view_hidden_records(user):
    if not user.is_top_level_admin:
        return False
    policy = AccessPolicy.objects.filter(id=1).first()
    if policy is None or policy.hidden_records_mode == HiddenRecordsMode.DENY_ALL:
        return False
    return (
        UserPermissionBridge.objects.active()
        .for_user(user)
        .filter(permission__code=HIDDEN_RECORDS)
        .exists()
    )


def codes_through_roles(user):
    return role_permission_codes(effective_role_ids(user))


def granted_codes(user):
    """What the person's roles and grants give them, whether or not the account is usable."""
    held = codes_through_roles(user)
    held |= set(Permission.objects.granted_to_user(user).values_list("code", flat=True))
    if user.is_top_level_admin:
        held |= set(Permission.objects.active().values_list("code", flat=True))
    held.discard(HIDDEN_RECORDS)
    if _may_view_hidden_records(user):
        held.add(HIDDEN_RECORDS)
    return held


def permission_codes(user, now):
    return granted_codes(user) if is_account_usable(user, now) else set()


def has_permission(user, code, now):
    return code in permission_codes(user, now)
