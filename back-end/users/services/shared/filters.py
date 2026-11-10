from dataclasses import dataclass

from accounts.models import User


@dataclass(frozen=True)
class UserFilter:
    q: str | None = None
    role: str | None = None
    status: str | None = None


def filtered_users(users_filter):
    users = User.objects.not_deleted().with_active_roles()
    if users_filter.q:
        users = users.search(users_filter.q)
    if users_filter.role:
        users = users.with_role(users_filter.role)
    if users_filter.status:
        users = users.with_status(users_filter.status)
    return users.newest_first()
