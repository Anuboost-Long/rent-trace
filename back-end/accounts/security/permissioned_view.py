from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.security.mfa_permission import MfaCompleted
from accounts.security.permission_required import HasRequiredPermission


class PermissionedView(APIView):
    """Signed in, two-step verification done, and holding the code listed for the HTTP method."""

    permission_classes = [IsAuthenticated, MfaCompleted, HasRequiredPermission]
    required_permissions: dict[str, str] = {}
