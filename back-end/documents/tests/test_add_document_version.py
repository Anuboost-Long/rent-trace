from documents.models import DocumentVersion
from documents.tests.base import DocumentApiTestCase
from reviews.models import ReviewRequest


class AddDocumentVersionTests(DocumentApiTestCase):
    def test_a_new_version_keeps_the_old_one_and_asks_for_confirmation_again(self):
        document = self.published()

        response = self.add_version(document)

        self.assertEqual(response.status_code, 201, response.data)
        first, second = response.data["versions"]
        self.assertEqual((first["version_no"], first["confirmation"]), (1, "SUPERSEDED"))
        self.assertEqual((second["version_no"], second["confirmation"]), (2, "WAITING"))
        self.assertEqual(DocumentVersion.objects.get(version_no=2).supersedes_version.version_no, 1)
        statuses = sorted(ReviewRequest.objects.values_list("status", flat=True))
        self.assertEqual(statuses, ["CANCELLED", "PENDING_REVIEW"])

    def test_a_report_version_becomes_current_immediately(self):
        document = self.published(document_type="CONDITION_REPORT")

        response = self.add_version(document)

        self.assertEqual(response.data["current_version_id"], response.data["versions"][1]["id"])

    def test_a_confirmed_version_stays_current_until_the_next_one_is_confirmed(self):
        document = self.published()
        self.answer(document["versions"][0]["id"], "confirm")

        response = self.add_version(document)

        self.assertEqual(response.data["current_version_id"], document["versions"][0]["id"])

    def test_only_the_owning_landlord_can_add_a_version(self):
        document = self.published()
        self.as_user(self.mia)
        other = self.client.post(
            f"/api/landlord/documents/{document['id']}/versions/",
            {"title": "x", "file": self.pdf()},
            format="multipart",
        )
        self.assertEqual(other.status_code, 404)
        self.as_user(self.tina)
        tenant = self.client.post(
            f"/api/landlord/documents/{document['id']}/versions/",
            {"title": "x", "file": self.pdf()},
            format="multipart",
        )
        self.assertEqual(tenant.status_code, 403)
