from rest_framework import serializers

from accounts.models import User, UserMfa
from users.resources.user_summary import UserSummaryResource


class UserDetailResource(UserSummaryResource):
    has_authenticator = serializers.SerializerMethodField()

    class Meta(UserSummaryResource.Meta):
        model = User
        fields = [
            *UserSummaryResource.Meta.fields,
            "phone_number",
            "auth_method",
            "has_authenticator",
        ]

    def get_has_authenticator(self, user) -> bool:
        return UserMfa.objects.confirmed().filter(user=user).exists()
