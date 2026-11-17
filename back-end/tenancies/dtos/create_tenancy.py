from rest_framework import serializers

from tenancies.dtos.terms_fields import TermsFieldsDto


class CreateTenancyDto(TermsFieldsDto):
    property_unit_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        end_date = attrs.get("end_date")
        if end_date and end_date <= attrs["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "End date must be after the start date."}
            )
        return attrs
