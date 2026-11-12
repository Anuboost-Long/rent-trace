from rest_framework import serializers

from properties.models import ListingStatus


class ChangeListingDto(serializers.Serializer):
    listing_status = serializers.ChoiceField(choices=ListingStatus.values)
