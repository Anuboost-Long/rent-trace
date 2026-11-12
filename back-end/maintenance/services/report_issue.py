from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from common.models import PartySide
from maintenance.models import MaintenanceIssue, MaintenanceStatus, MaintenanceTrigger
from maintenance.services.shared import notices
from maintenance.services.shared.history import record_transition
from tenancies.models import Tenancy, TenancyParty, TenancyStatus

NOT_STARTED = "You can only report an issue on a tenancy that has started and hasn't ended."


@transaction.atomic
def report_issue(*, user, fields):
    tenancy = (
        Tenancy.objects.live()
        .select_related("property_unit__property")
        .filter(pk=fields["tenancy_id"])
        .first()
    )
    is_member = tenancy is not None and (
        TenancyParty.objects.filter(tenancy=tenancy, tenant=user).current().exists()
    )
    if not is_member:
        raise NotFound("No tenancy with this id.")
    if tenancy.status != TenancyStatus.ACTIVE:
        raise ValidationError({"tenancy_id": NOT_STARTED})
    now = timezone.now()
    issue = MaintenanceIssue.objects.create(
        property_unit=tenancy.property_unit,
        tenancy=tenancy,
        title=fields["title"].strip(),
        description=fields["description"].strip(),
        priority=fields["priority"],
        status=MaintenanceStatus.REPORTED,
        reported_by=user,
        reporter_side=PartySide.TENANT,
        reported_at=now,
        created_by=user,
    )
    record_transition(
        issue, MaintenanceStatus.REPORTED, MaintenanceTrigger.REPORT, user, "Reported"
    )
    notices.reported(issue, user)
    return issue
