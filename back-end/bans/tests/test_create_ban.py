from datetime import timedelta

from django.utils import timezone

from accounts.models import AccountAccessHistory, AuthSession, Ban
from accounts.services.shared.account_rules import is_identity_banned
from users.tests.base import UsersApiTestCase


class CreateBanTests(UsersApiTestCase):
    def ban(self, **fields):
        return self.post("/api/bans/", {"reason": "Spam", **fields})

    def test_bans_an_email_and_blocks_it(self):
        admin = self.sign_in_as_admin(super_admin=True)

        response = self.ban(ban_type="EMAIL", value="  Spam@Example.com ")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["value"], "spam@example.com")
        self.assertEqual(response.data["status"], "ACTIVE")
        self.assertEqual(Ban.objects.get(pk=response.data["id"]).created_by, admin)
        self.assertTrue(is_identity_banned("spam@example.com", timezone.now()))

    def test_bans_a_domain_and_accepts_a_leading_at_sign(self):
        self.sign_in_as_admin(super_admin=True)

        response = self.ban(ban_type="EMAIL_DOMAIN", value="@Spam.example")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["value"], "spam.example")
        self.assertTrue(is_identity_banned("anyone@spam.example", timezone.now()))

    def test_bans_an_account_ends_its_sessions_and_records_history(self):
        admin = self.sign_in_as_admin(super_admin=True)
        user = self.make_user("ann@example.com")
        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 200)
        self.sign_in_user(admin)

        response = self.ban(ban_type="ACCOUNT", user_id=user.pk, reason="Abuse")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["id"], user.pk)
        self.assertFalse(AuthSession.objects.filter(user=user, revoked_at__isnull=True).exists())
        history = AccountAccessHistory.objects.get(user=user, action="ADMIN_BANNED_ACCOUNT")
        self.assertEqual((history.created_by, history.reason), (admin, "Abuse"))
        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 401)

    def test_a_ban_can_expire(self):
        self.sign_in_as_admin(super_admin=True)
        soon = (timezone.now() + timedelta(days=3)).isoformat()

        response = self.ban(ban_type="EMAIL", value="a@example.com", expires_at=soon)

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data["expires_at"])

    def test_rejects_bad_input(self):
        self.sign_in_as_admin(super_admin=True)
        past = (timezone.now() - timedelta(days=1)).isoformat()

        cases = [
            {"ban_type": "EMAIL", "value": "no-at-sign"},
            {"ban_type": "EMAIL", "value": ""},
            {"ban_type": "EMAIL_DOMAIN", "value": "a@b.com"},
            {"ban_type": "EMAIL_DOMAIN", "value": "localhost"},
            {"ban_type": "ACCOUNT"},
            {"ban_type": "PHONE", "value": "+85512345678"},
            {"ban_type": "EMAIL", "value": "a@example.com", "expires_at": past},
            {"ban_type": "EMAIL", "value": "a@example.com", "reason": ""},
        ]
        for body in cases:
            with self.subTest(body=body):
                self.assertEqual(self.ban(**body).status_code, 400)
        self.assertFalse(Ban.objects.exists())

    def test_the_same_target_cannot_be_banned_twice(self):
        self.sign_in_as_admin(super_admin=True)
        user = self.make_user("ann@example.com")

        for body in (
            {"ban_type": "EMAIL", "value": "a@example.com"},
            {"ban_type": "ACCOUNT", "user_id": user.pk},
        ):
            with self.subTest(body=body):
                self.assertEqual(self.ban(**body).status_code, 201)
                self.assertEqual(self.ban(**body).status_code, 400)

    def test_you_cannot_ban_yourself_or_the_super_admin(self):
        admin = self.sign_in_as_admin(super_admin=True)
        other = self.verified_user(email="other@example.com")
        self.give_roles(other, "ADMIN")
        self.sign_in_user(other)

        self.assertEqual(self.ban(ban_type="ACCOUNT", user_id=other.pk).status_code, 400)
        self.assertEqual(self.ban(ban_type="ACCOUNT", user_id=admin.pk).status_code, 403)

    def test_an_unknown_person_is_not_found(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.ban(ban_type="ACCOUNT", user_id=999999).status_code, 404)

    def test_needs_the_manage_permission(self):
        self.make_role("VIEWER", ["bans.view"])
        self.sign_in_as_admin(roles=("VIEWER",))

        self.assertEqual(self.ban(ban_type="EMAIL", value="a@example.com").status_code, 403)
