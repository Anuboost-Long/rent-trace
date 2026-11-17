from datetime import date, timedelta

from django.utils import timezone

from tenancies.models import Tenancy, TenancyParty
from tenancies.tests.base import TenancyApiTestCase

URL = "/api/maintenance/"


class MaintenanceApiTestCase(TenancyApiTestCase):
    """An active tenancy with Tina living in it, and a landlord (Lou) who owns the property."""

    _signed_in = None

    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(
            status="ACTIVE", start_date=timezone.now().date() - timedelta(days=30)
        )
        self.add_tenant(self.tenancy["id"], self.tina)
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        self._signed_in = None

    def as_user(self, user):
        if self._signed_in != user.pk:
            super().as_user(user)
            self._signed_in = user.pk

    def sign_in_as_admin(self, **kwargs):
        self._signed_in = None
        return super().sign_in_as_admin(**kwargs)

    def report(self, user=None, tenancy=None, **extra):
        self.as_user(user or self.tina)
        payload = {
            "tenancy_id": (tenancy or self.tenancy)["id"],
            "title": "Kitchen tap drips",
            "description": "It drips all night.",
            "priority": "MEDIUM",
            **extra,
        }
        return self.post(URL, payload)

    def reported(self, **extra):
        response = self.report(**extra)
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def act(self, issue, path, user, data=None):
        self.as_user(user)
        return self.post(f"{URL}{issue['id']}/{path}", data or {})

    def detail(self, issue, user):
        self.as_user(user)
        return self.client.get(f"{URL}{issue['id']}/")

    def propose(self, issue, user, outcome="FIXED", reason="It is sorted."):
        return self.act(issue, "closure/", user, {"outcome": outcome, "reason": reason})

    def answer(self, issue, user, how="approve"):
        proposal = self.detail(issue, user).data["open_closure"]
        return self.act(issue, f"closure/{proposal['id']}/{how}/", user)

    def add_co_tenant(self, user=None):
        return TenancyParty.objects.create(
            tenancy_id=self.tenancy["id"],
            tenant=user or self.sam,
            joined_at=date(2026, 12, 1),
        )
