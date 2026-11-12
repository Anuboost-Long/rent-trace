from notifications.models import Notification


def list_notifications(*, user, unread_only=False):
    inbox = Notification.objects.for_recipient(user)
    if unread_only:
        inbox = inbox.unread()
    return inbox.newest_first()
