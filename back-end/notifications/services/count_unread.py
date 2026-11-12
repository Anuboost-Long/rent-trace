from notifications.models import Notification


def count_unread(*, user):
    return Notification.objects.for_recipient(user).unread().count()
