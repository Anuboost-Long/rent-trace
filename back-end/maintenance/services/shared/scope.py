from django.db.models import Q
from rest_framework.exceptions import NotFound

from maintenance.models import MaintenanceIssue
from properties.services.shared.queries import live_properties
from tenancies.models import TenancyParty

NOT_FOUND = "No maintenance issue with this id."


def visible_issues(user):
    """Issues on tenancies the person has been a tenant of, and on properties they currently own.
    Someone who left a tenancy can still read its old issues."""
    ever_tenant = TenancyParty.objects.filter(tenant=user, deleted_at__isnull=True)
    return MaintenanceIssue.objects.filter(
        Q(tenancy__in=ever_tenant.values("tenancy_id"))
        | Q(property_unit__property__in=live_properties(user))
    ).with_details()


def find_issue(user, issue_id, *, lock=False):
    issues = visible_issues(user)
    if lock:
        issues = issues.select_for_update(of=("self",))
    found = issues.filter(pk=issue_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found
