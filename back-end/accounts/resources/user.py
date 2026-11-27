from rest_framework import serializers

from accounts.models import User
from accounts.services.shared.account_rules import is_admin_side


class UserResource(serializers.ModelSerializer):
    picture_id = serializers.IntegerField(
        source="avatar_file_id",
        allow_null=True,
        help_text="The profile picture's file id, or null. It changes when the picture does.",
    )
    roles = serializers.SerializerMethodField()
    role_names = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

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
            "is_top_level_admin",
            "roles",
            "role_names",
            "is_admin",
            "created_at",
            "last_login_at",
            "picture_id",
        ]

    def get_roles(self, user) -> list[str]:
        return list(
            user.role_bridges.active().order_by("role__code").values_list("role__code", flat=True)
        )

    def get_role_names(self, user) -> list[str]:
        return list(
            user.role_bridges.active().order_by("role__code").values_list("role__name", flat=True)
        )

    def get_is_admin(self, user) -> bool:
        return is_admin_side(user)
