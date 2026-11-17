from datetime import timedelta

from django.core import mail
from django.utils import timezone

from accounts.security import tokens
from tenancies.models import Tenancy, TenancyInvitation
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TenancyApiTestCase


class InviteTenantTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()

    def test_a_landlord_invites_an_email_and_it_is_sent_the_link(self):
        sent_before = len(mail.outbox)

        response = self.invite(self.tenancy, email="  New.Tenant@Example.com ")

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["email"], "new.tenant@example.com")
        self.assertEqual(response.data["status"], "PENDING")
        self.assertNotIn("token", str(response.data))
        saved = TenancyInvitation.objects.get()
        self.assertEqual(saved.created_by, self.lou)
        self.assertLess(
            abs(saved.expires_at - saved.created_at - timedelta(days=7)), timedelta(minutes=1)
        )
        self.assertEqual(len(mail.outbox), sent_before + 1)
        self.assertEqual(mail.outbox[-1].to, ["new.tenant@example.com"])
        self.assertEqual(saved.token_hash, tokens.digest(self.invitation_token()))

    def test_the_same_email_cannot_be_invited_twice_to_one_tenancy(self):
        self.invite(self.tenancy)

        again = self.invite(self.tenancy)

        self.assertIn("email", again.data)
        self.assertEqual(TenancyInvitation.objects.count(), 1)

    def test_a_current_tenant_cannot_be_invited(self):
        self.add_tenant(self.tenancy["id"], self.tina)

        response = self.invite(self.tenancy)

        self.assertIn("email", response.data)

    def test_only_one_primary_tenant(self):
        self.add_tenant(self.tenancy["id"], self.tina, is_primary=True)

        response = self.invite(self.tenancy, email="bob@example.com", is_primary=True)

        self.assertIn("is_primary", response.data)

    def test_an_ended_tenancy_takes_no_invitations(self):
        Tenancy.objects.update(status="ENDED")

        self.assertEqual(self.invite(self.tenancy).status_code, 400)

    def test_a_landlord_cannot_invite_to_someone_elses_tenancy(self):
        self.as_user(self.amy)

        response = self.post(
            f"{LANDLORD_URL}{self.tenancy['id']}/invitations/", {"email": "x@example.com"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(TenancyInvitation.objects.exists())

    def test_a_bad_email_is_rejected(self):
        self.assertIn("email", self.invite(self.tenancy, email="nope").data)

    def test_an_admin_can_invite_to_any_tenancy(self):
        self.sign_in_as_admin()

        response = self.post(
            f"{ADMIN_URL}{self.tenancy['id']}/invitations/", {"email": "bob@example.com"}
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(TenancyInvitation.objects.get().created_by.email, "admin@example.com")

    def test_tenants_cannot_invite(self):
        self.as_user(self.tina)

        response = self.post(
            f"{LANDLORD_URL}{self.tenancy['id']}/invitations/", {"email": "x@example.com"}
        )

        self.assertEqual(response.status_code, 403)


class ResendAndRevokeTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.invitation = self.invite(self.tenancy, email="bob@example.com").data
        self.first_token = self.invitation_token()
        self.base = f"{LANDLORD_URL}{self.tenancy['id']}/invitations/{self.invitation['id']}/"

    def test_resend_gives_a_new_link_and_stops_the_old_one(self):
        response = self.post(f"{self.base}resend/")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertNotEqual(self.invitation_token(), self.first_token)
        self.assertEqual(mail.outbox[-1].to, ["bob@example.com"])
        self.assertEqual(TenancyInvitation.objects.count(), 1)

    def test_an_expired_invitation_can_be_resent(self):
        TenancyInvitation.objects.update(expires_at=timezone.now())

        response = self.post(f"{self.base}resend/")

        self.assertEqual(response.data["status"], "PENDING")

    def test_revoke_ends_the_invitation_and_it_cannot_be_resent(self):
        revoked = self.post(f"{self.base}revoke/")

        self.assertEqual(revoked.data["status"], "REVOKED")
        self.assertEqual(self.post(f"{self.base}resend/").status_code, 404)
        self.assertEqual(self.post(f"{self.base}revoke/").status_code, 404)

    def test_a_revoked_email_can_be_invited_again(self):
        self.post(f"{self.base}revoke/")

        again = self.invite(self.tenancy, email="bob@example.com")

        self.assertEqual(again.status_code, 201, again.data)

    def test_another_landlord_cannot_resend_or_revoke(self):
        self.as_user(self.amy)

        self.assertEqual(self.post(f"{self.base}resend/").status_code, 404)
        self.assertEqual(self.post(f"{self.base}revoke/").status_code, 404)

    def test_the_tenancy_lists_its_invitations(self):
        response = self.client.get(f"{LANDLORD_URL}{self.tenancy['id']}/")

        self.assertEqual(
            [(i["email"], i["status"]) for i in response.data["invitations"]],
            [("bob@example.com", "PENDING")],
        )
