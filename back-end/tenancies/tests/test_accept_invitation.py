from django.utils import timezone

from accounts.models import User
from tenancies.models import Tenancy, TenancyInvitation, TenancyParty
from tenancies.tests.base import LANDLORD_URL, TENANT_URL, TenancyApiTestCase


class AcceptInvitationTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.invite(self.tenancy, email="tina@example.com")
        self.token = self.invitation_token()
        self.as_user(self.tina)

    def accept(self, token=None):
        return self.post(f"{TENANT_URL}accept/", {"token": token or self.token})

    def test_the_invited_tenant_joins_with_the_link(self):
        response = self.accept()

        self.assertEqual(response.status_code, 200, response.data)
        joined = TenancyParty.objects.get()
        self.assertEqual(
            (joined.tenant, joined.tenancy_id, joined.is_primary),
            (self.tina, self.tenancy["id"], False),
        )
        invitation = TenancyInvitation.objects.get()
        self.assertEqual((invitation.accepted_by, invitation.revoked_at), (self.tina, None))

    def test_the_link_works_once(self):
        self.accept()

        self.assertEqual(self.accept().status_code, 400)
        self.assertEqual(TenancyParty.objects.count(), 1)

    def test_a_forwarded_link_does_not_work_for_another_account(self):
        other = self.make_user("other@example.com", "TENANT")
        self.as_user(other)

        response = self.accept()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(TenancyParty.objects.exists())
        self.assertIsNone(TenancyInvitation.objects.get().accepted_at)

    def test_an_unverified_email_cannot_accept(self):
        User.objects.filter(pk=self.tina.pk).update(email_verified_at=None)

        self.assertEqual(self.accept().status_code, 400)
        self.assertFalse(TenancyParty.objects.exists())

    def test_expired_revoked_and_unknown_links_all_fail_the_same_way(self):
        TenancyInvitation.objects.update(expires_at=timezone.now())
        expired = self.accept()
        TenancyInvitation.objects.update(
            expires_at=timezone.now() + timezone.timedelta(days=1), revoked_at=timezone.now()
        )
        revoked = self.accept()
        unknown = self.accept(token="not-a-real-token")

        self.assertEqual({r.status_code for r in (expired, revoked, unknown)}, {400})
        self.assertEqual(expired.data, unknown.data)
        self.assertEqual(revoked.data, unknown.data)

    def test_a_primary_invitation_makes_the_tenant_primary(self):
        TenancyInvitation.objects.update(is_primary=True)

        self.accept()

        self.assertTrue(TenancyParty.objects.get().is_primary)

    def test_a_primary_invitation_conflicts_with_an_existing_primary(self):
        TenancyInvitation.objects.update(is_primary=True)
        self.add_tenant(
            self.tenancy["id"], self.make_user("pat@example.com", "TENANT"), is_primary=True
        )

        response = self.accept()

        self.assertEqual(response.status_code, 409)
        self.assertIsNone(TenancyInvitation.objects.get().accepted_at)

    def test_a_closed_tenancy_cannot_be_joined(self):
        Tenancy.objects.update(status="CANCELLED")

        self.assertEqual(self.accept().status_code, 400)

    def test_landlords_and_admins_cannot_accept(self):
        self.as_user(self.lou)
        self.assertEqual(self.accept().status_code, 403)

    def test_a_tenant_lists_and_accepts_by_id(self):
        listed = self.client.get(TENANT_URL)

        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(listed.data[0]["unit_name"], "Flat 1")
        self.assertEqual(listed.data[0]["invited_by"], "Lou Reed")
        self.assertNotIn("token", str(listed.data))

        accepted = self.post(f"{TENANT_URL}{listed.data[0]['id']}/accept/")

        self.assertEqual(accepted.status_code, 200, accepted.data)
        self.assertEqual(self.client.get(TENANT_URL).data, [])

    def test_the_list_only_shows_my_own_pending_invitations(self):
        other = self.make_user("other@example.com", "TENANT")
        self.as_user(other)

        self.assertEqual(self.client.get(TENANT_URL).data, [])
        self.assertEqual(
            self.post(f"{TENANT_URL}{TenancyInvitation.objects.get().pk}/accept/").status_code, 400
        )

    def test_the_landlord_sees_the_tenant_after_they_join(self):
        self.accept()
        self.as_user(self.lou)

        detail = self.client.get(f"{LANDLORD_URL}{self.tenancy['id']}/").data

        self.assertEqual([t["first_name"] for t in detail["tenants"]], ["Tina"])
        self.assertEqual(detail["invitations"][0]["status"], "ACCEPTED")
