from datetime import timedelta

from django.utils import timezone

from accounts.models import AccountAccessHistory, Ban
from accounts.services.shared.account_rules import is_identity_banned
from users.tests.base import UsersApiTestCase


class LiftBanTests(UsersApiTestCase):
    def make_ban(self, **fields):
        data = {"ban_type": "EMAIL", "value": "spam@example.com", "reason": "Spam"}
        return Ban.objects.create(**{**data, **fields})

    def lift(self, ban, reason="Mistake"):
        return self.post(f"/api/bans/{ban.pk}/lift/", {"reason": reason})

    def test_lifts_an_email_ban(self):
        admin = self.sign_in_as_admin(super_admin=True)
        ban = self.make_ban()
        self.assertTrue(is_identity_banned("spam@example.com", timezone.now()))

        response = self.lift(ban)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "LIFTED")
        self.assertEqual(response.data["lift_reason"], "Mistake")
        ban.refresh_from_db()
        self.assertEqual(ban.lifted_by, admin)
        self.assertFalse(is_identity_banned("spam@example.com", timezone.now()))

    def test_lifting_an_account_ban_lets_the_person_sign_in_and_records_history(self):
        admin = self.sign_in_as_admin(super_admin=True)
        user = self.make_user("ann@example.com")
        ban = self.make_ban(ban_type="ACCOUNT", value=None, user=user, reason="Abuse")
        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 401)
        self.sign_in_user(admin)

        self.lift(ban, "Resolved")

        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 200)
        history = AccountAccessHistory.objects.get(user=user, action="ADMIN_LIFTED_BAN")
        self.assertEqual((history.created_by, history.reason), (admin, "Resolved"))

    def test_a_reason_is_required(self):
        self.sign_in_as_admin(super_admin=True)
        ban = self.make_ban()

        self.assertEqual(self.lift(ban, reason="").status_code, 400)
        self.assertEqual(self.post(f"/api/bans/{ban.pk}/lift/", {}).status_code, 400)

    def test_an_ended_ban_cannot_be_lifted_again(self):
        self.sign_in_as_admin(super_admin=True)
        lifted = self.make_ban()
        self.lift(lifted)
        expired = self.make_ban(
            value="old@example.com", expires_at=timezone.now() + timedelta(seconds=1)
        )
        Ban.objects.filter(pk=expired.pk).update(
            created_at=timezone.now() - timedelta(hours=2),
            expires_at=timezone.now() - timedelta(hours=1),
        )

        self.assertEqual(self.lift(lifted).status_code, 400)
        self.assertEqual(self.lift(expired).status_code, 400)

    def test_unknown_ban_is_404(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.post("/api/bans/999999/lift/", {"reason": "x"}).status_code, 404)

    def test_viewing_is_not_enough_to_lift(self):
        self.make_role("VIEWER", ["bans.view"])
        self.sign_in_as_admin(roles=("VIEWER",))
        ban = self.make_ban()

        self.assertEqual(self.lift(ban).status_code, 403)
        self.assertEqual(self.client.get("/api/bans/").status_code, 200)

    def test_you_cannot_lift_the_ban_of_someone_who_can_do_more(self):
        self.limited_admin_role(without=("accounts.delete",))
        self.sign_in_as_admin(roles=("LIMITED",))
        boss = self.make_admin_user("boss@example.com", "ADMIN")
        ban = self.make_ban(ban_type="ACCOUNT", value=None, user=boss, reason="Test")

        self.assertEqual(self.lift(ban).status_code, 403)
        ban.refresh_from_db()
        self.assertIsNone(ban.lifted_at)
