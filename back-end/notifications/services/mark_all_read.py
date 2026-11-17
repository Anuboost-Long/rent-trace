from django.utils import timezone

from notifications.models import Notification


def mark_all_read(*, user):
    return Notification.objects.for_recipient(user).unread().update(read_at=timezone.now())
