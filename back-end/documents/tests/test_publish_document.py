from documents.models import Document
from documents.tests.base import PNG, DocumentApiTestCase
from files.models import File
from notifications.models import Notification
from reviews.models import ReviewRequest


class PublishDocumentTests(DocumentApiTestCase):
    def test_a_tenancy_agreement_waits_for_the_tenants_confirmation(self):
        response = self.publish()

        self.assertEqual(response.status_code, 201, response.data)
        version = response.data["versions"][0]
        self.assertEqual((version["version_no"], version["confirmation"]), (1, "WAITING"))
        self.assertIsNone(response.data["current_version_id"])
        self.assertEqual(version["files"][0]["name"], "agreement.pdf")
        request = ReviewRequest.objects.get(kind="DOCUMENT_CONFIRMATION")
        self.assertEqual(
            (request.review_route, request.requester_side), ("OPPOSITE_SIDE", "LANDLORD")
        )
        sent = Notification.objects.get(recipient=self.tina, kind="DOCUMENT_CONFIRMATION_REQUESTED")
        self.assertEqual(sent.subject_id, self.tenancy["id"])

    def test_a_report_needs_no_consent_and_is_current_at_once(self):
        response = self.publish(document_type="CONDITION_REPORT", title="Exit report")

        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data["versions"][0]["confirmation"])
        self.assertEqual(response.data["current_version_id"], response.data["versions"][0]["id"])
        self.assertFalse(ReviewRequest.objects.exists())
        self.assertTrue(
            Notification.objects.filter(recipient=self.tina, kind="DOCUMENT_ADDED").exists()
        )

    def test_a_receipt_is_linked_to_a_maintenance_issue_and_takes_its_tenancy(self):
        issue = self.issue()

        response = self.publish(
            document_type="RECEIPT",
            title="Plumber receipt",
            maintenance_issue_id=issue.pk,
            tenancy_id="",
            file=self.pdf("receipt.png", PNG),
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["maintenance_issue_id"], issue.pk)
        self.assertEqual(response.data["tenancy_id"], self.tenancy["id"])

    def test_a_tenancy_agreement_must_name_a_tenancy(self):
        response = self.publish(tenancy_id="")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Document.objects.exists())

    def test_only_pdfs_and_images_up_to_the_limit_are_accepted(self):
        self.assertEqual(self.publish(file=self.pdf("note.txt", b"hello")).status_code, 400)
        self.assertFalse(File.objects.exists())

    def test_the_unit_tenancy_and_issue_must_belong_together(self):
        self.assertEqual(self.publish(tenancy_id=9999).status_code, 404)
        self.assertEqual(
            self.publish(
                document_type="RECEIPT", maintenance_issue_id=9999, tenancy_id=""
            ).status_code,
            404,
        )

    def test_a_tenant_and_another_landlord_cannot_publish(self):
        self.assertEqual(self.publish(user=self.tina).status_code, 403)
        self.assertEqual(self.publish(user=self.mia).status_code, 404)
