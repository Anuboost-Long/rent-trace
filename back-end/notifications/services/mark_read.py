from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from notifications.models import Notification


@transaction.atomic
def mark_read(*, user, notification_id):
    found = (
        Notification.objects.for_recipient(user)
        .select_for_update()
        .filter(pk=notification_id)
        .first()
    )
    if found is None:
        raise NotFound("No notification with this id.")
    if found.read_at is None:
        found.read_at = timezone.now()
        found.save(update_fields=["read_at"])
    return found
