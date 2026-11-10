from django.utils import timezone

from accounts.models import AccountAccessHistory, AuthSession
from users.tests.base import UsersApiTestCase


class UserStatusTests(UsersApiTestCase):
    def deactivate(self, user_id):
        return self.post(f"/api/users/{user_id}/deactivate/")

    def activate(self, user_id):
        return self.post(f"/api/users/{user_id}/activate/")

    def test_deactivate_suspends_the_account_and_ends_their_sessions(self):
        admin = self.sign_in_as_admin()
        user = self.make_user("ann@example.com")
        self.client.credentials()
        ann_token = self.sign_in(email="ann@example.com").data["access_token"]
        self.authorize(self.sign_in(email=admin.email).data["access_token"])
        AuthSession.objects.filter(user=admin).update(mfa_verified_at=timezone.now())

        response = self.deactivate(user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["account_status"], "SUSPENDED")
        self.assertFalse(AuthSession.objects.filter(user=user, revoked_at__isnull=True).exists())
        self.client.credentials()
        self.authorize(ann_token)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 401)
        self.assertTrue(
            AccountAccessHistory.objects.filter(
                user=user, action="ADMIN_DEACTIVATED_ACCOUNT"
            ).exists()
        )

    def test_activate_restores_sign_in(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")
        self.deactivate(user.pk)

        response = self.activate(user.pk)

        self.assertEqual(response.data["account_status"], "ACTIVE")
        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 200)

    def test_repeating_an_action_changes_nothing_and_writes_no_history(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")

        self.activate(user.pk)
        self.deactivate(user.pk)
        self.deactivate(user.pk)

        self.assertEqual(AccountAccessHistory.objects.filter(user=user).count(), 1)

    def test_cannot_deactivate_yourself_or_the_super_admin(self):
        root = self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.deactivate(root.pk).status_code, 400)

    def test_an_admin_cannot_deactivate_someone_who_can_do_more(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))
        full_admin = self.make_admin_user("boss@example.com", "ADMIN")

        self.assertEqual(self.deactivate(full_admin.pk).status_code, 403)
        self.assertEqual(self.activate(full_admin.pk).status_code, 403)

    def test_peer_admins_can_deactivate_each_other(self):
        self.sign_in_as_admin()
        peer = self.make_admin_user("peer@example.com", "ADMIN")

        self.assertEqual(self.deactivate(peer.pk).status_code, 200)

    def test_super_admin_account_cannot_be_deactivated_by_another_admin(self):
        self.sign_in_as_admin(super_admin=True)
        other = self.make_user("deputy@example.com", role="ADMIN")
        from accounts.models import User

        User.objects.filter(pk=other.pk).update(is_top_level_admin=True)

        self.assertEqual(self.deactivate(other.pk).status_code, 403)


class SuspendedTargetTests(UsersApiTestCase):
    def test_a_suspended_admin_does_not_look_powerless(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))
        boss = self.make_admin_user("boss@example.com", "ADMIN")
        from accounts.models import User

        User.objects.filter(pk=boss.pk).update(account_status="SUSPENDED")

        response = self.post(f"/api/users/{boss.pk}/activate/")

        self.assertEqual(response.status_code, 403)
