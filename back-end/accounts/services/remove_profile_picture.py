from django.db import transaction

from accounts.models import User
from accounts.services.shared import account_management as manage
from accounts.services.shared.pictures import hide_file


@transaction.atomic
def remove_profile_picture(*, user):
    now = manage.now()
    target = (
        User.objects.select_for_update(of=("self",)).select_related("avatar_file").get(pk=user.pk)
    )
    before = target.avatar_file
    if before is None:
        return target
    target.avatar_file = None
    hide_file(before, target, now)
    manage.save_change(target, target, now)
    manage.record_change(
        actor=target,
        target=target,
        action="REMOVED_OWN_PICTURE",
        before={"picture_id": before.pk},
        after={"picture_id": None},
        reason="Profile picture removed by the account holder",
    )
    return target
