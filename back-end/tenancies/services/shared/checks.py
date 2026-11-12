from rest_framework.exceptions import ValidationError

from tenancies.models import TenancyParty


def check_can_invite(tenancy, email, is_primary):
    if TenancyParty.objects.filter(tenancy=tenancy).current().with_tenant_email(email).exists():
        raise ValidationError({"email": "This person is already a tenant here."})
    if tenancy.invitations.outstanding().with_email(email).exists():
        raise ValidationError({"email": "This email already has an invitation. Resend it instead."})
    if is_primary and TenancyParty.objects.filter(tenancy=tenancy).current().primary().exists():
        raise ValidationError({"is_primary": "This tenancy already has a primary tenant."})
