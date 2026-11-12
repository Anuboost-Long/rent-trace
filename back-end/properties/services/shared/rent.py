from rest_framework.exceptions import ValidationError


def check_rent(amount, frequency):
    if amount is not None and not frequency:
        raise ValidationError({"rent_frequency": "Choose how often the rent is paid."})
    if frequency and amount is None:
        raise ValidationError({"rent_amount": "Enter the rent amount."})
