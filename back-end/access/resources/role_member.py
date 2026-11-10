from rest_framework import serializers

from accounts.models import User


class RoleMemberResource(serializers.ModelSerializer):
    role_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role_names"]

    def get_role_names(self, user) -> list[str]:
        return [bridge.role.name for bridge in user.active_role_bridges]


class RoleMemberPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = RoleMemberResource(many=True)
