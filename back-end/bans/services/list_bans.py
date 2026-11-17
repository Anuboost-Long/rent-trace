from django.utils import timezone

from accounts.models import Ban


def list_bans(*, q=None, status=None, ban_type=None):
    bans = Ban.objects.with_people()
    if q:
        bans = bans.search(q)
    if status:
        bans = bans.with_status(status, timezone.now())
    if ban_type:
        bans = bans.with_type(ban_type)
    return bans.newest_first()
