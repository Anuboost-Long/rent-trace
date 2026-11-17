from django.utils import timezone

from accounts.models import AccountAccessHistory, AuthSession
from users.tests.base import UsersApiTestCase

URL = "/api/tokens/"


class TokenTests(UsersApiTestCase):
    def sign_in_elsewhere(self, email, device="iPhone"):
        token = self.sign_in(email=email).data["access_token"]
        AuthSession.objects.filter(user__email=email).update(
            device_name=device, ip_address="203.0.113.7"
        )
        return token

    def revoke(self, session, **body):
        return self.post(f"{URL}{session.pk}/revoke/", body)

    def test_lists_sessions_with_status_device_and_the_current_one_marked(self):
        admin = self.sign_in_as_admin(super_admin=True)
        ann = self.make_user("ann@example.com", first_name="Ann", last_name="Lee")
        self.client.credentials()
        self.sign_in_elsewhere(ann.email)
        self.sign_in_user(admin)

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        rows = {r["user"]["email"]: r for r in response.data["results"]}
        self.assertEqual(rows["ann@example.com"]["device_name"], "iPhone")
        self.assertEqual(rows["ann@example.com"]["ip_address"], "203.0.113.7")
        self.assertEqual(rows["ann@example.com"]["status"], "ACTIVE")
        self.assertFalse(rows["ann@example.com"]["is_current"])
        current = [r for r in response.data["results"] if r["is_current"]]
        self.assertEqual([r["user"]["id"] for r in current], [admin.pk])

    def test_filters_by_status_and_text(self):
        admin = self.sign_in_as_admin(super_admin=True)
        ann = self.make_user("ann@example.com", first_name="Ann", last_name="Lee")
        self.client.credentials()
        self.sign_in_elsewhere(ann.email, "Pixel 9")
        self.sign_in_user(admin)
        AuthSession.objects.filter(user=ann).update(revoked_at=timezone.now())

        revoked = self.client.get(URL, {"status": "REVOKED"}).data["results"]
        active = self.client.get(URL, {"status": "ACTIVE"}).data["results"]
        by_device = self.client.get(URL, {"q": "pixel"}).data["results"]

        self.assertEqual([r["user"]["email"] for r in revoked], ["ann@example.com"])
        self.assertNotIn("ann@example.com", [r["user"]["email"] for r in active])
        self.assertEqual(len(by_device), 1)

    def test_revoking_a_session_ends_that_access_token_and_records_history(self):
        admin = self.sign_in_as_admin(super_admin=True)
        ann = self.make_user("ann@example.com")
        self.client.credentials()
        ann_token = self.sign_in_elsewhere(ann.email)
        self.sign_in_user(admin)
        session = AuthSession.objects.get(user=ann)

        response = self.revoke(session, reason="Lost phone")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "REVOKED")
        self.client.credentials()
        self.authorize(ann_token)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        history = AccountAccessHistory.objects.get(user=ann, action="ADMIN_REVOKED_SESSION")
        self.assertEqual((history.created_by, history.reason), (admin, "Lost phone"))

    def test_revoking_twice_changes_nothing(self):
        admin = self.sign_in_as_admin(super_admin=True)
        ann = self.make_user("ann@example.com")
        self.client.credentials()
        self.sign_in_elsewhere(ann.email)
        self.sign_in_user(admin)
        session = AuthSession.objects.get(user=ann)

        self.revoke(session)
        self.revoke(session)

        self.assertEqual(AccountAccessHistory.objects.filter(user=ann).count(), 1)

    def test_you_cannot_revoke_the_session_you_are_using(self):
        admin = self.sign_in_as_admin(super_admin=True)
        current = AuthSession.objects.get(user=admin)

        self.assertEqual(self.revoke(current).status_code, 400)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)

    def test_unknown_session_is_404(self):
        self.sign_in_as_admin(super_admin=True)

        self.assertEqual(self.post(f"{URL}999999/revoke/", {}).status_code, 404)

    def test_viewing_is_not_enough_to_revoke(self):
        self.make_role("VIEWER", ["tokens.view"])
        self.sign_in_as_admin(roles=("VIEWER",))
        ann = self.make_user("ann@example.com")
        self.client.credentials()
        self.sign_in_elsewhere(ann.email)
        self.sign_in_user(self.make_admin_user("viewer2@example.com", "VIEWER"))
        session = AuthSession.objects.get(user=ann)

        self.assertEqual(self.client.get(URL).status_code, 200)
        self.assertEqual(self.revoke(session).status_code, 403)

    def test_you_cannot_revoke_sessions_of_someone_who_can_do_more(self):
        self.limited_admin_role()
        self.sign_in_as_admin(roles=("LIMITED",))
        boss = self.make_admin_user("boss@example.com", "ADMIN")
        self.client.credentials()
        self.sign_in_elsewhere(boss.email)
        self.sign_in_user(self.make_admin_user("lim2@example.com", "LIMITED"))
        session = AuthSession.objects.get(user=boss)

        self.assertEqual(self.revoke(session).status_code, 403)

    def test_needs_the_view_permission(self):
        self.make_role("CLERK", ["accounts.view"])
        self.sign_in_as_admin(roles=("CLERK",))

        self.assertEqual(self.client.get(URL).status_code, 403)
