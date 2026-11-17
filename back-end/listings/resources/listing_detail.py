from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from listings.resources.listing_summary import ListingSummaryResource, RentResource
from listings.services.shared.presentation import listed_by, public_photos, unit_photos


class ListingPhotoResource(serializers.Serializer):
    id = serializers.IntegerField(source="pk")
    unit_id = serializers.IntegerField(source="property_unit_id", allow_null=True)
    caption = serializers.CharField(allow_null=True)
    is_cover = serializers.BooleanField()


class ListingUnitResource(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    unit_type = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    occupancy_status = serializers.CharField()
    rent = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    @extend_schema_field(ListingPhotoResource(many=True))
    def get_photos(self, unit) -> list:
        return ListingPhotoResource(unit_photos(self.context["listing"], unit), many=True).data

    def get_rent(self, unit) -> dict | None:
        if unit.rent_amount is None:
            return None
        return RentResource({"amount": unit.rent_amount, "frequency": unit.rent_frequency}).data


class ListingDetailResource(ListingSummaryResource):
    public_description = serializers.CharField(allow_null=True)
    listed_by = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    units = serializers.SerializerMethodField()

    @extend_schema_field(ListingUnitResource(many=True))
    def get_units(self, listing) -> list:
        return ListingUnitResource(
            listing.public_units, many=True, context={"listing": listing}
        ).data

    def get_photos(self, listing) -> list:
        return ListingPhotoResource(public_photos(listing), many=True).data

    def get_listed_by(self, listing) -> str | None:
        return listed_by(listing)
