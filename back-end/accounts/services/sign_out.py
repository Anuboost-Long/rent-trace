from django.utils import timezone


def sign_out(session):
    session.revoked_at = timezone.now()
    session.save()
