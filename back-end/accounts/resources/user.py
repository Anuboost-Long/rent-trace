from rest_framework import serializers

from accounts.models import User


class UserResource(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "auth_method",
            "email_verified_at",
            "roles",
        ]

    def get_roles(self, user) -> list[str]:
        return list(user.role_bridges.active().values_list("role__code", flat=True))
