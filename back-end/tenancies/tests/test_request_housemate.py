from datetime import date

from django.core import mail
from django.utils import timezone

from notifications.models import Notification
from tenancies.models import Tenancy, TenancyInvitation, TenancyParty
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, HousemateApiTestCase


class RequestHousemateTests(HousemateApiTestCase):
    def test_a_tenant_asks_and_both_the_invitee_and_the_landlord_are_told(self):
        sent_before = len(mail.outbox)

        made = self.asked()

        saved = TenancyInvitation.objects.get(pk=made["id"])
        self.assertEqual((saved.requested_by_tenant, saved.created_by), (True, self.tina))
        self.assertIsNone(saved.landlord_decision)
        self.assertEqual(made["waiting_on"], ["LANDLORD", "INVITEE"])
        recipients = [message.to[0] for message in mail.outbox[sent_before:]]
        self.assertCountEqual(recipients, ["sam@example.com", "lou@example.com"])
        kinds = {row.recipient_id: row.kind for row in Notification.objects.all()}
        self.assertEqual(kinds[self.lou.pk], "TENANCY_HOUSEMATE_REQUESTED")
        self.assertEqual(kinds[self.sam.pk], "TENANCY_INVITATION_RECEIVED")

    def test_notifications_hold_no_email_address_or_link(self):
        self.asked()

        text = " ".join(row.title + row.body for row in Notification.objects.all())

        self.assertNotIn("@", text)
        self.assertNotIn("http", text)
        self.assertNotIn("token", text.lower())

    def test_the_reply_is_the_same_whether_or_not_the_address_has_an_account(self):
        known = self.ask("sam@example.com")
        unknown = self.ask("nobody@example.com")

        self.assertEqual((known.status_code, unknown.status_code), (201, 201))
        self.assertEqual(set(known.data), set(unknown.data))

    def test_only_current_tenants_of_that_tenancy_can_ask(self):
        outsider = self.ask(user=self.zed)
        self.assertEqual(outsider.status_code, 404)
        TenancyParty.objects.filter(tenant=self.tina).update(left_at=date(2026, 12, 20))
        self.assertEqual(self.ask().status_code, 404)

    def test_landlords_and_admins_cannot_use_the_tenant_endpoint(self):
        self.assertEqual(self.ask(user=self.lou).status_code, 403)
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.assertEqual(
            self.post(
                f"/api/tenant/tenancies/{self.tenancy['id']}/invitations/", {"email": "a@b.com"}
            ).status_code,
            403,
        )

    def test_cannot_ask_on_an_ended_or_cancelled_tenancy(self):
        for status in ("ENDED", "CANCELLED"):
            with self.subTest(status=status):
                Tenancy.objects.filter(pk=self.tenancy["id"]).update(status=status)
                self.assertEqual(self.ask().status_code, 400)

    def test_rejects_your_own_email_a_current_tenant_and_a_duplicate(self):
        self.add_tenant(self.tenancy["id"], self.zed)
        self.asked("sam@example.com")

        for email in ("tina@example.com", "zed@example.com", "sam@example.com"):
            with self.subTest(email=email):
                response = self.ask(email)
                self.assertEqual(response.status_code, 400)
                self.assertIn("email", response.data)

    def test_at_most_five_requests_wait_at_once(self):
        for number in range(5):
            self.asked(f"guest{number}@example.com")

        response = self.ask("guest5@example.com")

        self.assertEqual(response.status_code, 400)
        self.assertIn("5 requests", str(response.data))

    def test_withdrawing_and_asking_again_still_hits_the_daily_limit(self):
        for number in range(10):
            made = self.asked(f"guest{number}@example.com")
            self.assertEqual(self.withdraw(made).status_code, 200)

        response = self.ask("guest10@example.com")

        self.assertEqual(response.status_code, 400)
        self.assertIn("today", str(response.data))

    def test_requests_older_than_a_day_do_not_count(self):
        for number in range(10):
            made = self.asked(f"guest{number}@example.com")
            self.withdraw(made)
        TenancyInvitation.objects.update(created_at=timezone.now() - timezone.timedelta(days=2))
        TenancyInvitation.objects.update(expires_at=timezone.now() - timezone.timedelta(days=1))

        self.assertEqual(self.ask("fresh@example.com").status_code, 201)

    def test_a_landlords_own_invitation_still_needs_only_the_invitee(self):
        self.as_user(self.lou)
        made = self.post(
            f"{LANDLORD_URL}{self.tenancy['id']}/invitations/", {"email": "sam@example.com"}
        )

        saved = TenancyInvitation.objects.get(pk=made.data["id"])
        self.assertEqual((saved.requested_by_tenant, saved.landlord_decision), (False, "APPROVED"))
        self.assertEqual(made.data["waiting_on"], ["INVITEE"])
        self.assertEqual(self.accept(made.data).status_code, 200)
        self.assertTrue(self.is_tenant(self.sam))

    def test_an_admin_invitation_is_approved_by_the_admin(self):
        admin = self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        made = self.post(
            f"{ADMIN_URL}{self.tenancy['id']}/invitations/", {"email": "sam@example.com"}
        )

        saved = TenancyInvitation.objects.get(pk=made.data["id"])

        self.assertEqual((saved.landlord_decision, saved.landlord_decided_by), ("APPROVED", admin))
