from rest_framework import serializers

from accounts.models import AccountStatus


class UserFilterDto(serializers.Serializer):
    q = serializers.CharField(
        required=False, max_length=100, help_text="Words to find in the email or name."
    )
    role = serializers.CharField(required=False, max_length=30, help_text="A role code.")
    status = serializers.ChoiceField(choices=AccountStatus.values, required=False)


class UserListQueryDto(UserFilterDto):
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False, min_value=1, max_value=100, help_text="Up to 100. Default 20."
    )
