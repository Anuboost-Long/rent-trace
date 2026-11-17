from django.utils import timezone

from accounts.models import AuthSession


def list_tokens(*, q=None, status=None):
    sessions = AuthSession.objects.with_user()
    if q:
        sessions = sessions.search(q)
    if status:
        sessions = sessions.with_status(status, timezone.now())
    return sessions.newest_first()
