import uuid

from django.db import transaction
from rest_framework.exceptions import ValidationError

from maintenance.services.shared import notices
from maintenance.services.shared.rules import acting_landlord, require_open
from maintenance.services.shared.scope import find_issue
from providers.models import MaintenanceAssignment, PropertyServiceProvider

NOT_ON_PROPERTY = "Choose a tradesperson you have linked to this property."


@transaction.atomic
def assign_provider(*, user, issue_id, service_provider_id, scheduled_at=None, as_admin=False):
    issue = find_issue(user, issue_id, lock=True, as_admin=as_admin)
    owner = acting_landlord(issue, user, as_admin=as_admin) or user
    require_open(issue)
    link = (
        PropertyServiceProvider.objects.filter(
            property=issue.property_unit.property_id,
            service_provider_id=service_provider_id,
            service_provider__owner=owner,
            service_provider__deleted_at__isnull=True,
            deleted_at__isnull=True,
        )
        .select_related("service_provider")
        .first()
    )
    if link is None:
        raise ValidationError({"service_provider_id": NOT_ON_PROPERTY})
    previous = issue.assignments.filter(superseded_by__isnull=True).first()
    assignment = MaintenanceAssignment.objects.create(
        maintenance_issue=issue,
        service_provider=link.service_provider,
        supersedes_assignment=previous,
        recorded_by=user,
        scheduled_at=scheduled_at,
        created_by=user,
        correlation_id=uuid.uuid4(),
    )
    notices.provider_assigned(issue, link.service_provider, scheduled_at)
    return assignment
