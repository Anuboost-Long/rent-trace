from notifications.models import Notification


def notify(recipients, *, kind, title, body, subject_id=None):
    """Writes one inbox row per person. Call it inside the action's own transaction."""
    people = {person.pk: person for person in recipients}
    Notification.objects.bulk_create(
        Notification(recipient=person, kind=kind, title=title, body=body, subject_id=subject_id)
        for person in people.values()
    )
