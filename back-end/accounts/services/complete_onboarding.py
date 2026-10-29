from django.db import transaction

from rest_framework.exceptions import ValidationError

from accounts.services.shared.account_rules import assign_role, has_active_role


@transaction.atomic
def complete_onboarding(*, user, first_name, last_name, role_code):
    if has_active_role(user):
        raise ValidationError("Onboarding is already complete.")
    user.first_name, user.last_name = first_name, last_name
    user.save()
    assign_role(user, role_code)
