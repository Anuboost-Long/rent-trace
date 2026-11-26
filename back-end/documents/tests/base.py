import shutil
import tempfile
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

from maintenance.models import MaintenanceIssue
from tenancies.tests.base import TenancyApiTestCase

LANDLORD_URL = "/api/landlord/documents/"
ADMIN_URL = "/api/admin/documents/"
PDF = b"%PDF-1.4\n" + b"\x00" * 64
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class DocumentApiTestCase(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        self.tenancy = self.new_tenancy()
        self.add_tenant(self.tenancy["id"], self.tina)
        self.mia = self.make_user("mia@example.com", "LANDLORD", "Mia", "Cole")
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")

    @property
    def tenant_url(self):
        return f"/api/tenant/tenancies/{self.tenancy['id']}/documents/"

    def pdf(self, name="agreement.pdf", content=PDF):
        return SimpleUploadedFile(name, content)

    def publish(self, user=None, **extra):
        self.as_user(user or self.lou)
        fields = {
            "unit_id": self.unit.pk,
            "document_type": "TENANCY_AGREEMENT",
            "title": "Tenancy agreement",
            "tenancy_id": self.tenancy["id"],
            "file": self.pdf(),
            **extra,
        }
        return self.client.post(LANDLORD_URL, fields, format="multipart")

    def published(self, **extra):
        response = self.publish(**extra)
        assert response.status_code == 201, response.data
        return response.data

    def add_version(self, document, title="Agreement v2", **extra):
        self.as_user(self.lou)
        return self.client.post(
            f"{LANDLORD_URL}{document['id']}/versions/",
            {"title": title, "file": self.pdf("v2.pdf"), **extra},
            format="multipart",
        )

    def answer(self, version_id, action, user=None, key=None, **extra):
        self.as_user(user or self.tina)
        return self.post(
            f"{self.tenant_url}versions/{version_id}/{action}/",
            {"idempotency_key": str(key or uuid.uuid4()), **extra},
        )

    def issue(self):
        return MaintenanceIssue.objects.create(
            property_unit=self.unit,
            tenancy_id=self.tenancy["id"],
            title="Leaking tap",
            description="Kitchen tap drips.",
            priority="MEDIUM",
            reported_by=self.tina,
            reporter_side="TENANT",
            reported_at=timezone.now(),
            created_by=self.tina,
        )
