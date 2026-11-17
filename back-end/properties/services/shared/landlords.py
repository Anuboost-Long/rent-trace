from rest_framework.exceptions import ValidationError

from accounts.models import AccountStatus, User


def active_landlords():
    return (
        User.objects.not_deleted()
        .with_status(AccountStatus.ACTIVE)
        .with_role("LANDLORD")
        .distinct()
    )


def find_landlord(owner_id):
    landlord = active_landlords().filter(pk=owner_id).first()
    if landlord is None:
        raise ValidationError({"owner_id": "Choose an active landlord."})
    return landlord
