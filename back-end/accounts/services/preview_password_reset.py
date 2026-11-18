from django.utils import timezone

from accounts.models import AuthTokenPurpose, UserMfa
from accounts.services.shared.links import usable_link


def preview_password_reset(raw_token):
    """Says whether the reset also needs an authenticator code, without using the link up."""
    link = usable_link(raw_token, AuthTokenPurpose.PASSWORD_RESET, timezone.now())
    return {"requires_code": UserMfa.objects.confirmed().filter(user=link.user).exists()}
