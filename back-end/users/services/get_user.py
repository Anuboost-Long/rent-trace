from rest_framework.exceptions import NotFound

from accounts.models import User


def get_user(*, user_id):
    user = User.objects.not_deleted().with_active_roles().filter(pk=user_id).first()
    if user is None:
        raise NotFound("No user with this id.")
    return user
