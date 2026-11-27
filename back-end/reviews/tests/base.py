import uuid
from datetime import timedelta

from django.utils import timezone

from reviews.models import ReviewRequest
from tenancies.tests.base import TenancyApiTestCase

LANDLORD_URL = "/api/landlord/condition-evidence/"
ADMIN_URL = "/api/admin/review-cases/"


class EvidenceApiTestCase(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.add_tenant(self.tenancy["id"], self.tina)
        self.mia = self.make_user("mia@example.com", "LANDLORD", "Mia", "Cole")
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")

    @property
    def tenant_url(self):
        return f"/api/tenant/tenancies/{self.tenancy['id']}/condition-evidence/"

    def evidence_fields(self, **extra):
        return {
            "title": "Damp patch in the bedroom",
            "description": "Wall near the window.",
            "observed_at": "2026-12-02T00:00:00Z",
            **extra,
        }

    def submit(self, user=None, **extra):
        self.as_user(user or self.tina)
        return self.post(self.tenant_url, self.evidence_fields(**extra))

    def submitted(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def approve(self, evidence, user=None, key=None):
        self.as_user(user or self.lou)
        return self.post(
            f"{LANDLORD_URL}{evidence['id']}/approve/",
            {"idempotency_key": str(key or uuid.uuid4())},
        )

    def reject(self, evidence, user=None, key=None, **extra):
        self.as_user(user or self.lou)
        payload = {
            "idempotency_key": str(key or uuid.uuid4()),
            "reason": "Not what I saw.",
            **extra,
        }
        return self.post(f"{LANDLORD_URL}{evidence['id']}/reject/", payload)

    def expire(self, evidence):
        ReviewRequest.objects.filter(pk=evidence["id"]).update(
            submitted_at=timezone.now() - timedelta(days=15)
        )

    def escalate(self, evidence, user, reason="Please decide."):
        self.as_user(user)
        if user in (self.lou, self.mia):
            url = f"{LANDLORD_URL}{evidence['id']}/escalate/"
        else:
            url = f"{self.tenant_url}{evidence['id']}/escalate/"
        return self.post(url, {"reason": reason})

    def admin_decides(self, case_id, action, key=None, reason="Seen the photos."):
        return self.post(
            f"{ADMIN_URL}{case_id}/{action}/",
            {"idempotency_key": str(key or uuid.uuid4()), "reason": reason},
        )

    def ask(self, evidence, user=None, key=None, reason="Which wall, and when?"):
        self.as_user(user or self.lou)
        return self.post(
            f"{LANDLORD_URL}{evidence['id']}/request-information/",
            {"idempotency_key": str(key or uuid.uuid4()), "reason": reason},
        )

    def respond(self, evidence, user=None, **fields):
        self.as_user(user or self.tina)
        payload = {"message": "The north wall, last Tuesday.", **fields}
        return self.post(f"{self.tenant_url}{evidence['id']}/respond/", payload)

    def shown_note(self):
        """A landlord note that tenants can see."""
        self.as_user(self.lou)
        created = self.post(
            "/api/landlord/conditions/",
            {
                "unit_id": self.unit.pk,
                "title": "Kitchen benchtop",
                "description": "Small chip near the sink.",
                "observed_at": "2026-11-13T00:00:00Z",
                "is_shown_to_tenants": True,
            },
        )
        assert created.status_code == 201, created.data
        return created.data

    def correction_fields(self, record_id, **extra):
        return {
            "record_id": record_id,
            "what_is_incorrect": "There is no chip.",
            "proposed_replacement": "Benchtop in good condition.",
            "why_change_needed": "I checked the photos at move-in.",
            **extra,
        }

    def ask_tenant_correction(self, record_id, user=None, **extra):
        self.as_user(user or self.tina)
        url = f"/api/tenant/tenancies/{self.tenancy['id']}/condition-corrections/"
        return self.post(url, self.correction_fields(record_id, **extra))

    def decide_correction(
        self, request_id, action, key=None, reason="Checked the inspection report."
    ):
        return self.post(
            f"/api/admin/condition-corrections/{request_id}/{action}/",
            {"idempotency_key": str(key or uuid.uuid4()), "reason": reason},
        )
