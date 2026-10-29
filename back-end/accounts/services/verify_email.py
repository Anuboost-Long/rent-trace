from django.db import transaction
from django.utils import timezone

from accounts.models import AuthTokenPurpose
from accounts.services.shared.links import use_link


@transaction.atomic
def verify_email(raw_token):
    now = timezone.now()
    user = use_link(raw_token, AuthTokenPurpose.EMAIL_VERIFICATION, now)
    if user.email_verified_at is None:
        user.email_verified_at = now
        user.save()
