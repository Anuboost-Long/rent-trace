from users.services.shared.filters import filtered_users


def list_users(*, users_filter):
    return filtered_users(users_filter)
