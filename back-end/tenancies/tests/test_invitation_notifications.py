from accounts.models import User
from notifications.models import Notification
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TENANT_URL, TenancyApiTestCase


class InvitationNotificationTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()

    def rows_for(self, person):
        return list(Notification.objects.filter(recipient=person).order_by("id"))

    def test_a_verified_tenant_with_that_email_is_told_without_the_link(self):
        invited = self.invite(self.tenancy)

        (row,) = self.rows_for(self.tina)

        self.assertEqual(invited.status_code, 201)
        self.assertEqual(row.kind, "TENANCY_INVITATION_RECEIVED")
        self.assertEqual(row.subject_id, invited.data["id"])
        self.assertIn("Lou Reed", row.body)
        self.assertNotIn("token", (row.title + row.body).lower())
        self.assertNotIn("http", row.body)

    def test_the_inviters_reply_is_the_same_whether_or_not_the_person_has_an_account(self):
        known = self.invite(self.tenancy, email="tina@example.com")
        unknown = self.invite(self.tenancy, email="nobody@example.com")

        self.assertEqual(known.status_code, unknown.status_code)
        self.assertEqual(set(known.data), set(unknown.data))

    def test_no_notification_for_an_unknown_unverified_or_non_tenant_email(self):
        User.objects.filter(pk=self.tina.pk).update(email_verified_at=None)

        self.invite(self.tenancy, email="tina@example.com")
        self.invite(self.tenancy, email="nobody@example.com")
        self.invite(self.tenancy, email="amy@example.com")

        self.assertEqual(Notification.objects.count(), 0)

    def test_resending_tells_them_again(self):
        invited = self.invite(self.tenancy)
        self.as_user(self.lou)
        self.post(f"{LANDLORD_URL}{self.tenancy['id']}/invitations/{invited.data['id']}/resend/")

        titles = [row.title for row in self.rows_for(self.tina)]

        self.assertEqual(titles, ["You're invited to join a tenancy", "Invitation sent again"])

    def test_a_failed_invite_makes_no_notification(self):
        self.invite(self.tenancy)
        sent = Notification.objects.count()

        self.assertEqual(self.invite(self.tenancy).status_code, 400)

        self.assertEqual(Notification.objects.count(), sent)

    def test_accepting_tells_the_landlord_who_invited(self):
        self.invite(self.tenancy)
        token = self.invitation_token()
        self.as_user(self.tina)

        accepted = self.post(f"{TENANT_URL}accept/", {"token": token})

        self.assertEqual(accepted.status_code, 200, accepted.data)
        row = self.rows_for(self.lou)[-1]
        self.assertEqual(row.kind, "TENANCY_INVITATION_ACCEPTED")
        self.assertEqual(row.subject_id, self.tenancy["id"])
        self.assertIn("Tina Ray", row.body)

    def test_accepting_tells_an_admin_who_invited_on_a_landlords_behalf(self):
        admin = self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.post(f"{ADMIN_URL}{self.tenancy['id']}/invitations/", {"email": "tina@example.com"})
        token = self.invitation_token()
        self.as_user(self.tina)

        self.post(f"{TENANT_URL}accept/", {"token": token})

        self.assertEqual(
            [row.kind for row in self.rows_for(admin)], ["TENANCY_INVITATION_ACCEPTED"]
        )

    def test_a_refused_accept_makes_no_notification(self):
        self.invite(self.tenancy)
        token = self.invitation_token()
        sent = Notification.objects.filter(recipient=self.lou).count()
        self.as_user(self.make_user("sam@example.com", "TENANT", "Sam", "Fox"))

        self.assertEqual(self.post(f"{TENANT_URL}accept/", {"token": token}).status_code, 400)

        self.assertEqual(Notification.objects.filter(recipient=self.lou).count(), sent)
