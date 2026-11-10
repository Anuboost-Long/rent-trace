from users.services.shared.filters import filtered_users

ALL_USERS_LIMIT = 500


def list_all_users(*, users_filter):
    return list(filtered_users(users_filter)[:ALL_USERS_LIMIT])
