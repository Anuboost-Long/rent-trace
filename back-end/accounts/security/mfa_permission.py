from rest_framework.permissions import BasePermission

from accounts.services.shared.mfa import MfaStatus, mfa_status

MFA_PENDING = (MfaStatus.ENROL, MfaStatus.VERIFY)


class MfaCompleted(BasePermission):
    message = "Finish two-step verification to use this."

    def has_permission(self, request, view):
        return mfa_status(request.auth) not in MFA_PENDING
