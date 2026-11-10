from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from accounts.services.shared.permissions import permission_codes

CANT_GIVE_WHAT_YOU_LACK = "You can't give access you don't have yourself."
CANT_ACT_ON_MORE_POWERFUL = "You can't manage someone who can do more than you can."


def ensure_holds(actor, codes, message=CANT_GIVE_WHAT_YOU_LACK):
    if actor.is_top_level_admin:
        return
    missing = set(codes) - permission_codes(actor, timezone.now())
    if missing:
        raise PermissionDenied(f"{message} Missing: {sorted(missing)}.")
