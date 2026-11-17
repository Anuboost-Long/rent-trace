from rest_framework import serializers

from accounts.models import User


class UserOptionResource(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "roles"]

    def get_roles(self, user) -> list[str]:
        return [bridge.role.code for bridge in user.active_role_bridges]
