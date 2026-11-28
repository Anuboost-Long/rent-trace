from documents.models import Document
from documents.tests.base import LANDLORD_URL, PNG, DocumentApiTestCase
from notifications.models import Notification


class TenantUploadTests(DocumentApiTestCase):
    def upload(self, user=None, tenancy_id=None, **extra):
        self.as_user(user or self.tina)
        fields = {
            "document_type": "RECEIPT",
            "title": "Plumber receipt",
            "file": self.pdf("receipt.pdf"),
            **extra,
        }
        url = f"/api/tenant/tenancies/{tenancy_id or self.tenancy['id']}/documents/"
        return self.client.post(url, fields, format="multipart")

    def test_a_tenant_uploads_a_receipt_and_it_is_current_at_once(self):
        response = self.upload()

        self.assertEqual(response.status_code, 201, response.data)
        version = response.data["versions"][0]
        self.assertEqual((version["title"], version["confirmation"]), ("Plumber receipt", None))
        self.assertEqual(response.data["current_version_id"], version["id"])
        self.assertEqual(Document.objects.get().created_by, self.tina)

    def test_the_landlord_sees_it_and_is_told_but_the_tenant_is_not(self):
        self.upload()

        sent = Notification.objects.get(kind="DOCUMENT_ADDED")
        self.assertEqual(sent.recipient, self.lou)
        self.assertEqual(sent.subject_id, self.tenancy["id"])
        self.as_user(self.lou)
        listed = self.client.get(f"{LANDLORD_URL}?unit_id={self.unit.pk}")
        self.assertEqual(len(listed.data), 1)

    def test_a_housemate_sees_it_too(self):
        self.add_tenant(self.tenancy["id"], self.sam)
        self.upload()

        self.as_user(self.sam)
        listed = self.client.get(f"/api/tenant/tenancies/{self.tenancy['id']}/documents/")

        self.assertEqual(len(listed.data), 1)

    def test_papers_that_need_consent_are_refused(self):
        for kind in ("TENANCY_AGREEMENT", "CONDITION_REPORT"):
            self.assertEqual(self.upload(document_type=kind).status_code, 400)
        self.assertFalse(Document.objects.exists())

    def test_a_notice_and_other_papers_are_allowed(self):
        self.assertEqual(self.upload(document_type="NOTICE").status_code, 201)
        self.assertEqual(
            self.upload(document_type="OTHER", file=self.pdf("b.pdf")).status_code, 201
        )

    def test_a_receipt_can_be_linked_to_an_issue_on_the_same_tenancy(self):
        issue = self.issue()

        response = self.upload(maintenance_issue_id=issue.pk)

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["maintenance_issue_id"], issue.pk)

    def test_an_issue_from_another_tenancy_is_not_found(self):
        issue = self.issue()
        issue.tenancy_id = None
        issue.save()

        self.assertEqual(self.upload(maintenance_issue_id=issue.pk).status_code, 404)
        self.assertEqual(self.upload(maintenance_issue_id=999999).status_code, 404)

    def test_someone_outside_the_tenancy_gets_a_404_and_nothing_is_stored(self):
        response = self.upload(user=self.sam)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Document.objects.exists())

    def test_a_landlord_cannot_use_the_tenant_route(self):
        self.assertIn(self.upload(user=self.lou).status_code, (403, 404))

    def test_a_wrong_file_type_is_refused(self):
        response = self.upload(file=self.pdf("notes.pdf", content=b"not a pdf at all"))

        self.assertEqual(response.status_code, 400)

    def test_a_png_photo_of_a_receipt_is_accepted(self):
        response = self.upload(file=self.pdf("receipt.png", content=PNG))

        self.assertEqual(response.status_code, 201, response.data)
