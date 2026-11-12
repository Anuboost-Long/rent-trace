from rest_framework import serializers

from tenancies.dtos.terms_fields import TermsFieldsDto


class UpdateTenancyDto(TermsFieldsDto):
    """Any of these may be sent; what is left out stays as it is. Send null to clear."""

    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
