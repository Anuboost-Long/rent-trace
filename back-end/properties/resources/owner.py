from rest_framework import serializers

from accounts.models import User
from properties.models import PropertyOwner


class OwnerOptionResource(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class OwnerResource(serializers.ModelSerializer):
    owner = OwnerOptionResource()

    class Meta:
        model = PropertyOwner
        fields = ["owner", "is_primary_owner", "ownership_percentage", "valid_from"]
