from decimal import Decimal

from rest_framework import serializers

from properties.models import RentFrequency

MIN_AMOUNT = Decimal("0.01")


class TermsFieldsDto(serializers.Serializer):
    """The money terms, shared by creating and editing a tenancy."""

    rent_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=MIN_AMOUNT,
        required=False,
        allow_null=True,
        help_text="Per payment, in Australian dollars. Needs a frequency.",
    )
    rent_frequency = serializers.ChoiceField(
        choices=RentFrequency.values, required=False, allow_null=True, allow_blank=True
    )
    bond_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=MIN_AMOUNT, required=False, allow_null=True
    )
