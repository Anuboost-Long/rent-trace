from django.utils import timezone

from accounts.models import User
from users.tests.base import UsersApiTestCase


class GetUserTests(UsersApiTestCase):
    def setUp(self):
        super().setUp()
        self.sign_in_as_admin(super_admin=True)

    def test_returns_the_detail_without_secrets(self):
        user = self.make_user("ann@example.com", role="LANDLORD")

        response = self.client.get(f"/api/users/{user.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "ann@example.com")
        self.assertEqual(response.data["roles"], ["LANDLORD"])
        self.assertIn("auth_method", response.data)
        self.assertFalse({"password", "password_hash", "ip_address"} & set(response.data))

    def test_missing_user_is_404(self):
        self.assertEqual(self.client.get("/api/users/999999/").status_code, 404)

    def test_soft_deleted_user_is_404(self):
        user = self.make_user("gone@example.com")
        User.objects.filter(pk=user.pk).update(deleted_at=timezone.now())

        self.assertEqual(self.client.get(f"/api/users/{user.pk}/").status_code, 404)
