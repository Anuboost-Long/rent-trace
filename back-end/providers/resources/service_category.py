from rest_framework import serializers

from providers.models import ServiceCategory


class ServiceCategoryResource(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["code", "name"]
