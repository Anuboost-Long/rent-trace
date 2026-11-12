from decimal import Decimal

WEEKS_PER_YEAR = Decimal(52)
MONTHS_PER_YEAR = Decimal(12)


def weekly_rent(amount, frequency):
    """Rent as a weekly figure so units paid on different schedules can be compared."""
    if amount is None:
        return None
    if frequency == "FORTNIGHTLY":
        return amount / 2
    if frequency == "MONTHLY":
        return amount * MONTHS_PER_YEAR / WEEKS_PER_YEAR
    return amount
