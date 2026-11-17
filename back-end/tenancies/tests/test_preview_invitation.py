from django.utils import timezone

from tenancies.models import TenancyInvitation
from tenancies.tests.base import TENANT_URL, TenancyApiTestCase


class PreviewInvitationTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.invite(self.tenancy, email="tina@example.com")
        self.token = self.invitation_token()
        self.as_user(self.tina)

    def preview(self, token=None):
        return self.client.get(f"{TENANT_URL}preview/", {"token": token or self.token})

    def test_shows_the_property_unit_and_who_invited(self):
        response = self.preview()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["unit_name"], self.unit.name)
        self.assertEqual(response.data["invited_by"], "Lou Reed")

    def test_does_not_accept_the_invitation(self):
        self.preview()

        self.assertIsNone(TenancyInvitation.objects.get().accepted_at)

    def test_expired_revoked_and_unknown_links_all_fail_the_same_way(self):
        TenancyInvitation.objects.update(expires_at=timezone.now())
        expired = self.preview()
        TenancyInvitation.objects.update(
            expires_at=timezone.now() + timezone.timedelta(days=1), revoked_at=timezone.now()
        )
        revoked = self.preview()
        unknown = self.preview(token="not-a-real-token")

        for response in (expired, revoked, unknown):
            self.assertEqual(response.status_code, 404, response.data)
