from django.db import transaction

from accounts.models import User
from accounts.services.shared import account_management as manage

PROFILE_FIELDS = ("first_name", "last_name", "phone_number")


@transaction.atomic
def update_profile(*, user, changes):
    now = manage.now()
    target = User.objects.select_for_update().get(pk=user.pk)
    before, after = {}, {}
    for field in PROFILE_FIELDS:
        if field not in changes:
            continue
        new_value = changes[field] or None if field == "phone_number" else changes[field]
        old_value = getattr(target, field)
        if new_value != old_value:
            before[field], after[field] = old_value, new_value
            setattr(target, field, new_value)
    if not after:
        return target
    manage.save_change(target, target, now)
    manage.record_change(
        actor=target,
        target=target,
        action="UPDATED_OWN_PROFILE",
        before=before,
        after=after,
        reason="Profile updated by the account holder",
    )
    return target
