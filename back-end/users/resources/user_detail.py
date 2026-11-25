from rest_framework import serializers

from accounts.models import User, UserMfa
from users.resources.user_summary import UserSummaryResource
from users.services.resend_authenticator_notice import was_reset


class UserDetailResource(UserSummaryResource):
    has_authenticator = serializers.SerializerMethodField()
    authenticator_was_reset = serializers.SerializerMethodField()

    class Meta(UserSummaryResource.Meta):
        model = User
        fields = [
            *UserSummaryResource.Meta.fields,
            "phone_number",
            "auth_method",
            "has_authenticator",
            "authenticator_was_reset",
        ]

    def get_has_authenticator(self, user) -> bool:
        return UserMfa.objects.confirmed().filter(user=user).exists()

    def get_authenticator_was_reset(self, user) -> bool:
        return was_reset(user)
