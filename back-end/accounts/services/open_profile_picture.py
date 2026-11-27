from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from accounts.models import User
from accounts.services.shared.account_rules import is_admin_side
from accounts.services.shared.relations import may_see_picture

NOT_FOUND = "No picture for this person."


def open_profile_picture(*, viewer, user_id):
    """The person, an admin, or someone they share a tenancy with; everyone else gets a 404."""
    target = User.objects.not_deleted().select_related("avatar_file").filter(pk=user_id).first()
    picture = target.avatar_file if target else None
    if picture is None or picture.deleted_at is not None:
        raise NotFound(NOT_FOUND)
    if not may_see_picture(viewer, target, viewer_is_admin=is_admin_side(viewer)):
        raise NotFound(NOT_FOUND)
    if not default_storage.exists(picture.object_key):
        raise NotFound(NOT_FOUND)
    return picture, default_storage.open(picture.object_key, "rb")
