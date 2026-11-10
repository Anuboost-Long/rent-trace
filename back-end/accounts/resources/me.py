from django.utils import timezone
from rest_framework import serializers

from accounts.resources.user import UserResource
from accounts.services.shared.mfa import MfaStatus, mfa_status
from accounts.services.shared.permissions import permission_codes


class MeResource(UserResource):
    mfa_status = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta(UserResource.Meta):
        fields = [*UserResource.Meta.fields, "mfa_status", "permissions"]

    def get_mfa_status(self, user) -> MfaStatus:
        return mfa_status(self.context["session"])

    def get_permissions(self, user) -> list[str]:
        return sorted(permission_codes(user, timezone.now()))
