from accounts.models import Permission, Role, UserRoleBridge

MAX_ROLE_DEPTH = 5


def role_ids_with_ancestors(role_ids):
    """The given roles plus their parents, stopping at any inactive role."""
    found = set()
    frontier = set(role_ids)
    for _ in range(MAX_ROLE_DEPTH + 1):
        rows = list(Role.objects.active().filter(pk__in=frontier).values_list("pk", "parent_id"))
        found |= {role_id for role_id, _ in rows}
        frontier = {parent for _, parent in rows if parent and parent not in found}
        if not frontier:
            break
    return found


def effective_role_ids(user):
    held = UserRoleBridge.objects.active().for_user(user).values_list("role_id", flat=True)
    return role_ids_with_ancestors(set(held))


def role_permission_codes(role_ids):
    return set(Permission.objects.granted_to_roles(role_ids).values_list("code", flat=True))


def role_effective_codes(role):
    return role_permission_codes(role_ids_with_ancestors({role.pk}))


def descendant_role_ids(role_ids):
    """The given roles plus every active role that inherits from them."""
    found = set(role_ids)
    frontier = set(role_ids)
    for _ in range(MAX_ROLE_DEPTH):
        children = set(
            Role.objects.active().filter(parent_id__in=frontier).values_list("pk", flat=True)
        )
        frontier = children - found
        if not frontier:
            break
        found |= frontier
    return found
