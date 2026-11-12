from django.db import migrations
from django.db.models import F


def approve_existing(apps, _schema_editor):
    """Every invitation so far came from a landlord or admin, so the landlord side already said yes."""
    Invitation = apps.get_model("tenancies", "TenancyInvitation")
    Invitation.objects.update(
        landlord_decision="APPROVED",
        landlord_decided_at=F("created_at"),
        landlord_decided_by=F("created_by"),
    )
    Invitation.objects.filter(accepted_at__isnull=False).update(
        invitee_accepted_at=F("accepted_at"), invitee_accepted_by=F("accepted_by")
    )


class Migration(migrations.Migration):
    dependencies = [("tenancies", "0002_housemate_approvals")]

    operations = [migrations.RunPython(approve_existing, migrations.RunPython.noop)]
