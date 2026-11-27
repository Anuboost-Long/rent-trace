import uuid

from documents.models import Document
from documents.tests.base import DocumentApiTestCase
from history.models import BusinessChangeHistory
from notifications.models import Notification
from reviews.models import ReviewRequest


class ConfirmDocumentTests(DocumentApiTestCase):
    def test_a_tenant_confirms_and_the_version_becomes_current(self):
        document = self.published()
        version_id = document["versions"][0]["id"]

        response = self.answer(version_id, "confirm")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["current_version_id"], version_id)
        self.assertEqual(response.data["versions"][0]["confirmation"], "CONFIRMED")
        history = BusinessChangeHistory.objects.get(action="CONFIRM_DOCUMENT_VERSION")
        self.assertEqual(
            (history.before_values, history.after_values),
            ({"current_version": None}, {"current_version": 1}),
        )
        sent = Notification.objects.get(recipient=self.lou, kind="DOCUMENT_CONFIRMATION_ANSWERED")
        self.assertEqual(sent.subject_id, self.tenancy["id"])

    def test_a_tenant_flags_it_with_a_reason_and_it_stays_unconfirmed(self):
        document = self.published()
        version_id = document["versions"][0]["id"]

        self.assertEqual(self.answer(version_id, "flag", reason="  ").status_code, 400)
        response = self.answer(version_id, "flag", reason="The rent is wrong.")

        self.assertEqual(response.data["versions"][0]["confirmation"], "FLAGGED")
        self.assertEqual(response.data["versions"][0]["flag_reason"], "The rent is wrong.")
        self.assertIsNone(response.data["current_version_id"])
        self.assertEqual(Document.objects.get().current_version, None)

    def test_a_version_is_answered_once_and_a_retry_changes_nothing(self):
        document = self.published()
        version_id = document["versions"][0]["id"]
        key = uuid.uuid4()
        self.answer(version_id, "confirm", key=key)

        self.assertEqual(self.answer(version_id, "confirm", key=key).status_code, 200)
        self.assertEqual(self.answer(version_id, "flag", reason="Too late").status_code, 400)
        self.assertEqual(BusinessChangeHistory.objects.count(), 1)

    def test_a_superseded_version_cannot_be_confirmed(self):
        document = self.published()
        first = document["versions"][0]["id"]
        self.add_version(document)

        self.assertEqual(self.answer(first, "confirm").status_code, 400)

    def test_a_document_that_needs_no_consent_has_nothing_to_confirm(self):
        document = self.published(document_type="NOTICE", title="Inspection notice")

        self.assertEqual(self.answer(document["versions"][0]["id"], "confirm").status_code, 404)

    def test_strangers_the_landlord_and_other_tenancies_are_refused(self):
        document = self.published()
        version_id = document["versions"][0]["id"]
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(self.answer(version_id, "confirm", user=self.lou).status_code, 403)
        outsider = self.make_user("out@example.com", "TENANT", "Out", "Sider")
        self.assertEqual(self.answer(version_id, "confirm", user=outsider).status_code, 404)
        self.assertEqual(ReviewRequest.objects.get().status, "PENDING_REVIEW")
        self.assertEqual(self.answer(version_id, "confirm", user=self.sam).status_code, 200)
