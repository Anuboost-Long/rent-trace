from django.db.models import Q
from django.utils import timezone

from accounts.models import RoleKind, User
from accounts.services.shared.permissions import has_permission

ADMIN_REVIEW = "reviews.admin_review"
REVIEW_REMOVAL = "reviews.review_removal"


def admins_who_hold(code):
    candidates = (
        User.objects.filter(deleted_at__isnull=True)
        .filter(
            Q(is_top_level_admin=True)
            | Q(role_bridges__is_active=True, role_bridges__role__kind=RoleKind.ADMIN)
        )
        .distinct()
    )
    now = timezone.now()
    return [admin for admin in candidates if has_permission(admin, code, now)]


def admins_who_can_decide():
    return admins_who_hold(ADMIN_REVIEW)


def admins_who_can_decide_removals():
    return admins_who_hold(REVIEW_REMOVAL)
