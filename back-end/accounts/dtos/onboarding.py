from rest_framework import serializers

from accounts.dtos.fields import SELF_SERVICE_ROLES


class OnboardingDto(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(choices=SELF_SERVICE_ROLES)
