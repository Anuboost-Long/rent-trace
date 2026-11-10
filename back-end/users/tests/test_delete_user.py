from django.utils import timezone

from accounts.models import AccountAccessHistory, AuthSession, User
from users.tests.base import UsersApiTestCase


class DeleteUserTests(UsersApiTestCase):
    def test_soft_deletes_and_ends_sessions(self):
        admin = self.sign_in_as_admin()
        user = self.make_user("ann@example.com")
        self.client.credentials()
        self.sign_in(email="ann@example.com")
        self.authorize(self.sign_in(email=admin.email).data["access_token"])
        AuthSession.objects.filter(user=admin).update(mfa_verified_at=timezone.now())

        response = self.client.delete(f"/api/users/{user.pk}/")

        self.assertEqual(response.status_code, 204)
        user.refresh_from_db()
        self.assertIsNotNone(user.deleted_at)
        self.assertEqual(user.deleted_by, admin)
        self.assertEqual(self.client.get(f"/api/users/{user.pk}/").status_code, 404)
        emails = [u["email"] for u in self.client.get("/api/users/").data["results"]]
        self.assertNotIn("ann@example.com", emails)
        self.assertFalse(AuthSession.objects.filter(user=user, revoked_at__isnull=True).exists())
        self.client.credentials()
        self.assertEqual(self.sign_in(email="ann@example.com").status_code, 401)
        self.assertTrue(
            AccountAccessHistory.objects.filter(user=user, action="ADMIN_DELETED_ACCOUNT").exists()
        )

    def test_deleting_twice_is_404(self):
        self.sign_in_as_admin()
        user = self.make_user("ann@example.com")
        self.client.delete(f"/api/users/{user.pk}/")

        self.assertEqual(self.client.delete(f"/api/users/{user.pk}/").status_code, 404)

    def test_cannot_delete_yourself(self):
        root = self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.client.delete(f"/api/users/{root.pk}/").status_code, 400)
        self.assertFalse(User.objects.get(pk=root.pk).deleted_at)

    def test_an_admin_cannot_delete_someone_who_can_do_more(self):
        self.limited_admin_role(without=("accounts.view",))
        self.sign_in_as_admin(roles=("LIMITED",))
        full_admin = self.make_admin_user("boss@example.com", "ADMIN")

        self.assertEqual(self.client.delete(f"/api/users/{full_admin.pk}/").status_code, 403)

    def test_tenant_cannot_delete(self):
        user = self.make_user("ann@example.com")
        self.authorize(self.sign_in(email=user.email).data["access_token"])

        self.assertEqual(self.client.delete(f"/api/users/{user.pk}/").status_code, 403)
