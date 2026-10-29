from django.db import transaction
from django.utils import timezone

from accounts.integrations import emails
from accounts.models import AuthTokenPurpose, User
from accounts.services.shared.account_rules import normalize_email
from accounts.services.shared.links import RESET_LINK_LIFETIME, issue_link
from accounts.services.shared.mail import send_after_commit


@transaction.atomic
def request_password_reset(email):
    now = timezone.now()
    user = User.objects.with_email(normalize_email(email)).password_accounts().not_deleted().first()
    if user is None:
        return
    raw = issue_link(user, AuthTokenPurpose.PASSWORD_RESET, RESET_LINK_LIFETIME, now)
    send_after_commit(emails.send_password_reset, user, raw)
