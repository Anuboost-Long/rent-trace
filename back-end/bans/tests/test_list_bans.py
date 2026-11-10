from datetime import timedelta

from django.utils import timezone

from accounts.models import Ban
from users.tests.base import UsersApiTestCase

URL = "/api/bans/"


class ListBansTests(UsersApiTestCase):
    def make_ban(self, **fields):
        data = {"ban_type": "EMAIL", "value": "spam@example.com", "reason": "Spam"}
        return Ban.objects.create(**{**data, **fields})

    def test_lists_bans_newest_first_with_status_and_person(self):
        self.sign_in_as_admin(super_admin=True)
        user = self.make_user("ann@example.com", first_name="Ann", last_name="Lee")
        now = timezone.now()
        self.make_ban(value="old@example.com")
        self.make_ban(ban_type="ACCOUNT", value=None, user=user, reason="Abuse")
        self.make_ban(value="gone@example.com", expires_at=now + timedelta(seconds=1))
        Ban.objects.filter(value="gone@example.com").update(
            created_at=now - timedelta(hours=2), expires_at=now - timedelta(hours=1)
        )

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data), {"count", "page", "page_size", "total_pages", "results"}
        )
        by_target = {(b["value"] or b["user"]["email"]): b for b in response.data["results"]}
        self.assertEqual(by_target["ann@example.com"]["status"], "ACTIVE")
        self.assertEqual(by_target["ann@example.com"]["user"]["first_name"], "Ann")
        self.assertEqual(by_target["gone@example.com"]["status"], "EXPIRED")
        self.assertIsNone(response.data["results"][0]["value"])
        self.assertEqual(response.data["results"][-1]["value"], "gone@example.com")

    def test_filters_by_status_type_and_text(self):
        self.sign_in_as_admin(super_admin=True)
        user = self.make_user("ann@example.com")
        self.make_ban(value="spam@example.com", reason="Sends spam")
        self.make_ban(ban_type="EMAIL_DOMAIN", value="bad.example", reason="Bad domain")
        self.make_ban(ban_type="ACCOUNT", value=None, user=user, reason="Abuse")
        Ban.objects.filter(value="spam@example.com").update(
            lifted_at=timezone.now(), lifted_by=user, lift_reason="Mistake"
        )

        lifted = self.client.get(URL, {"status": "LIFTED"}).data["results"]
        domains = self.client.get(URL, {"type": "EMAIL_DOMAIN"}).data["results"]
        by_person = self.client.get(URL, {"q": "ann"}).data["results"]
        by_reason = self.client.get(URL, {"q": "sends spam"}).data["results"]

        self.assertEqual([b["value"] for b in lifted], ["spam@example.com"])
        self.assertEqual([b["value"] for b in domains], ["bad.example"])
        self.assertEqual([b["ban_type"] for b in by_person], ["ACCOUNT"])
        self.assertEqual([b["value"] for b in by_reason], ["spam@example.com"])

    def test_pages_split_the_results(self):
        self.sign_in_as_admin(super_admin=True)
        for index in range(3):
            self.make_ban(value=f"u{index}@example.com")

        response = self.client.get(URL, {"page_size": 2})

        self.assertEqual((len(response.data["results"]), response.data["total_pages"]), (2, 2))

    def test_needs_the_view_permission(self):
        self.make_role("CLERK", ["accounts.view"])
        self.sign_in_as_admin(roles=("CLERK",))

        self.assertEqual(self.client.get(URL).status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.get(URL).status_code, 401)
