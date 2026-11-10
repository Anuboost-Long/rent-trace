from rest_framework import serializers


class AddRoleMemberDto(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
