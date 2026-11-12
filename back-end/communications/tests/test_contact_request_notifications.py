from datetime import timedelta

from django.utils import timezone

from communications.tests.base import LANDLORD_URL, TENANT_URL, ContactRequestApiTestCase
from notifications.models import Notification
from properties.models import PropertyOwner


class ContactRequestNotificationTests(ContactRequestApiTestCase):
    def kinds_for(self, person):
        rows = Notification.objects.filter(recipient=person).order_by("id")
        return [row.kind for row in rows]

    def test_sending_a_request_tells_the_owner_with_no_contact_details(self):
        made = self.asked()

        row = Notification.objects.get(recipient=self.lou)

        self.assertEqual(row.kind, "CONTACT_REQUEST_RECEIVED")
        self.assertEqual(row.subject_id, made["id"])
        self.assertIn("Tina Ray", row.body)
        self.assertNotIn("tina@example.com", row.title + row.body)
        self.assertFalse(Notification.objects.filter(recipient=self.tina).exists())

    def test_every_current_owner_is_told_but_not_other_landlords(self):
        PropertyOwner.objects.create(
            property_id=self.made["id"],
            owner=self.amy,
            valid_from=timezone.now() - timedelta(days=1),
        )

        self.asked()

        self.assertEqual(self.kinds_for(self.lou), ["CONTACT_REQUEST_RECEIVED"])
        self.assertEqual(self.kinds_for(self.amy), ["CONTACT_REQUEST_RECEIVED"])
        bob = self.make_user("bob@example.com", "LANDLORD", "Bob", "Day")
        self.assertEqual(self.kinds_for(bob), [])

    def test_the_tenant_is_told_when_accepted_declined_or_revoked(self):
        accepted = self.asked()
        self.answer(accepted, "accept")
        self.answer(accepted, "revoke")
        declined_tenant = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        declined = self.asked(declined_tenant)
        self.answer(declined, "decline")

        self.assertEqual(
            self.kinds_for(self.tina), ["CONTACT_REQUEST_ACCEPTED", "CONTACT_REQUEST_REVOKED"]
        )
        self.assertEqual(self.kinds_for(declined_tenant), ["CONTACT_REQUEST_DECLINED"])

    def test_nothing_in_a_notification_carries_the_landlords_contact_details(self):
        made = self.asked()
        self.answer(made, "accept")
        self.answer(made, "revoke")

        text = " ".join(
            row.title + row.body for row in Notification.objects.filter(recipient=self.tina)
        )

        self.assertNotIn("lou@example.com", text)
        self.assertNotIn("0400", text)
        self.assertIn("Lou Reed", text)

    def test_cancelling_tells_the_owner(self):
        made = self.asked()
        self.as_user(self.tina)
        self.post(f"{TENANT_URL}{made['id']}/cancel/")

        self.assertEqual(
            self.kinds_for(self.lou), ["CONTACT_REQUEST_RECEIVED", "CONTACT_REQUEST_CANCELLED"]
        )

    def test_a_refused_move_makes_no_notification(self):
        made = self.asked()
        sent = Notification.objects.count()

        self.assertEqual(self.answer(made, "revoke").status_code, 400)

        self.assertEqual(Notification.objects.count(), sent)

    def test_a_request_that_fails_leaves_no_notification(self):
        self.asked()
        sent = Notification.objects.count()

        self.assertEqual(self.ask().status_code, 400)

        self.assertEqual(Notification.objects.count(), sent)
        self.as_user(self.lou)
        self.assertEqual(self.client.get(LANDLORD_URL).status_code, 200)
