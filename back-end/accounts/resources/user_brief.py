from rest_framework import serializers

from accounts.models import User


class UserBriefResource(serializers.ModelSerializer):
    picture_id = serializers.IntegerField(source="avatar_file_id", allow_null=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "picture_id"]
