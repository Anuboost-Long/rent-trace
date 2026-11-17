from rest_framework import serializers

from listings.services.shared.presentation import cheapest_unit, cover_of, public_photos, title_of


class RentResource(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    frequency = serializers.CharField()


class ListingSummaryResource(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.SerializerMethodField()
    property_type = serializers.CharField()
    suburb = serializers.CharField()
    state = serializers.CharField()
    postcode = serializers.CharField()
    cover_file_id = serializers.SerializerMethodField()
    photo_count = serializers.SerializerMethodField()
    unit_count = serializers.IntegerField(source="public_unit_count")
    from_rent = serializers.SerializerMethodField()

    def get_title(self, listing) -> str:
        return title_of(listing)

    def get_cover_file_id(self, listing) -> int | None:
        cover = cover_of(listing)
        return cover.pk if cover else None

    def get_photo_count(self, listing) -> int:
        return len(public_photos(listing))

    def get_from_rent(self, listing) -> dict | None:
        unit = cheapest_unit(listing)
        if unit is None:
            return None
        return RentResource({"amount": unit.rent_amount, "frequency": unit.rent_frequency}).data
